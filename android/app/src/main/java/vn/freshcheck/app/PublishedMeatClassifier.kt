// SPDX-License-Identifier: MIT
// FreshCheck integration is MIT; published model attribution is in THIRD_PARTY_NOTICES.md.
package vn.freshcheck.app

import android.content.Context
import android.graphics.Bitmap
import android.os.SystemClock
import ai.onnxruntime.OnnxJavaType
import ai.onnxruntime.OnnxTensor
import ai.onnxruntime.OrtEnvironment
import ai.onnxruntime.OrtSession
import ai.onnxruntime.TensorInfo
import org.json.JSONObject
import java.io.File
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.nio.FloatBuffer
import java.security.MessageDigest

/** ONNX RGB classifier; model provenance and preprocessing are explicit in its config. */
class PublishedMeatClassifier(context: Context, configAsset: String = "published_model_config.json") : Classifier {
    private val config=JSONObject(context.assets.open(configAsset).bufferedReader().use { it.readText() })
    override val version=config.getString("version")
    override val sha256=config.getString("model_sha256")
    override val foods=config.getJSONArray("food_types").let { a -> List(a.length()) { a.getString(it) } }
    private val modelFile = config.optString("model_file", "published_meat.onnx")
    private val cropMode = config.getString("crop")
    private val threshold=config.getDouble("threshold").toFloat()
    private val env=OrtEnvironment.getEnvironment()
    private val session: OrtSession
    init {
        require(config.getString("runtime")=="onnx" && config.getInt("schema_version")==1)
        require(config.getInt("input_size")==224 && cropMode in setOf("resize_shorter_256_center_224", "stretch_224"))
        require(modelFile in setOf("published_meat.onnx", "fruitq_float32.onnx"))
        require((0..2).map { config.getJSONArray("labels").getString(it) }==Decision.labels)
        require(threshold in 0f..1f && foods.isNotEmpty())
        // Stream to app-private storage to avoid a second large model byte array in Java heap.
        val directory=File(context.noBackupFilesDir,"models").apply { mkdirs() }
        val file=File(directory,modelFile)
        val digest=MessageDigest.getInstance("SHA-256")
        context.assets.open(modelFile).use { input ->
            file.outputStream().use { out ->
                val buffer=ByteArray(65536)
                while(true) { val n=input.read(buffer); if(n<0) break; digest.update(buffer,0,n);out.write(buffer,0,n) }
            }
        }
        val actual=digest.digest().joinToString("") { "%02x".format(it.toInt() and 255) }
        require(actual==sha256) { "Model ONNX không khớp SHA-256." }
        session=OrtSession.SessionOptions().use { opts ->
            opts.setIntraOpNumThreads(4);opts.setInterOpNumThreads(1)
            env.createSession(file.absolutePath,opts)
        }
        try {
            val input=session.inputInfo["rgb"]!!.info as TensorInfo
            val output=session.outputInfo["probabilities"]!!.info as TensorInfo
            require(input.shape.contentEquals(longArrayOf(1,224,224,3)) && input.type==OnnxJavaType.FLOAT)
            require(output.shape.contentEquals(longArrayOf(1,3)))
        } catch(e:Exception) { session.close();throw e }
    }
    override fun preview(bitmap:Bitmap):Bitmap {
        if(cropMode == "stretch_224") return Bitmap.createScaledBitmap(bitmap,224,224,true)
        val w=bitmap.width;val h=bitmap.height
        val nw=if(w<=h) 256 else (w.toLong()*256/h).toInt()
        val nh=if(h<=w) 256 else (h.toLong()*256/w).toInt()
        val resized=Bitmap.createScaledBitmap(bitmap,nw,nh,true)
        // Python round uses ties-to-even; Math.rint matches it for CenterCrop offsets.
        val left=Math.rint((nw-224)/2.0).toInt();val top=Math.rint((nh-224)/2.0).toInt()
        return Bitmap.createBitmap(resized,left,top,224,224)
    }
    private fun input(bitmap:Bitmap):FloatBuffer {
        val crop=preview(bitmap);val pixels=IntArray(224*224)
        crop.getPixels(pixels,0,224,0,0,224,224)
        val values=ByteBuffer.allocateDirect(224*224*3*4).order(ByteOrder.nativeOrder()).asFloatBuffer()
        for(p in pixels) {values.put(((p shr 16) and 255).toFloat());values.put(((p shr 8) and 255).toFloat());values.put((p and 255).toFloat())}
        values.rewind();return values
    }
    private fun invoke(tensor:OnnxTensor):Pair<FloatArray,Double> {
        val start=SystemClock.elapsedRealtimeNanos()
        session.run(mapOf("rgb" to tensor)).use { output ->
            val elapsed=(SystemClock.elapsedRealtimeNanos()-start)/1e6
            @Suppress("UNCHECKED_CAST")
            val scores=(output[0].value as Array<FloatArray>)[0].copyOf()
            return scores to elapsed
        }
    }
    override fun classify(bitmap:Bitmap):Prediction {
        val start=SystemClock.elapsedRealtimeNanos()
        OnnxTensor.createTensor(env,input(bitmap),longArrayOf(1,224,224,3)).use { tensor ->
            val (scores,ms)=invoke(tensor)
            return Prediction(scores,Decision.choose(scores,threshold),ms,(SystemClock.elapsedRealtimeNanos()-start)/1e6)
        }
    }
    override fun benchmark(bitmap:Bitmap):List<Double> {
        OnnxTensor.createTensor(env,input(bitmap),longArrayOf(1,224,224,3)).use { tensor ->
            repeat(10) { invoke(tensor) }
            return List(100) { invoke(tensor).second }
        }
    }
    override fun close()=session.close()
}
