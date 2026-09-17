// SPDX-License-Identifier: MIT
// Copyright (c) 2026 FreshCheck contributors; see LICENSE.
package vn.freshcheck.app

import android.graphics.BitmapFactory
import android.graphics.Bitmap
import android.graphics.Color
import android.net.Uri
import android.os.SystemClock
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.Spinner
import android.widget.TextView
import androidx.test.core.app.ActivityScenario
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import java.io.File

@RunWith(AndroidJUnit4::class)
class ReleaseTest {
    private val instrumentation get() = InstrumentationRegistry.getInstrumentation()
    private val context get() = instrumentation.targetContext
    private fun children(v: View): List<View> = listOf(v) + if(v is ViewGroup) (0 until v.childCount).flatMap { children(v.getChildAt(it)) } else emptyList()
    private fun button(a: MainActivity, label: String) = children(a.window.decorView).filterIsInstance<Button>().first { it.text.toString()==label }
    private fun ready(s: ActivityScenario<MainActivity>) {
        repeat(300) {
            var ready=false
            s.onActivity { ready=button(it,"Chụp ảnh").isEnabled }
            if(ready) return
            SystemClock.sleep(200)
        }
        fail("UI remained busy for 60 seconds")
    }
    private fun fixture(name: String): File {
        val f=File(context.cacheDir,name)
        instrumentation.context.assets.open(name).use { i -> f.outputStream().use { i.copyTo(it) } }
        return f
    }
    private fun load(s: ActivityScenario<MainActivity>, file: File) {
        s.onActivity { a -> MainActivity::class.java.getDeclaredMethod("loadImage",Uri::class.java).apply { isAccessible=true }.invoke(a,Uri.fromFile(file)) }
        ready(s)
    }
    @Test fun nativeMeatAndFruitModelsLoadAndInfer() {
        for((config,photo) in listOf("published_model_config.json" to "meat.jpg","fruit_model_config.json" to "fruit.png")) {
            PublishedMeatClassifier(context,config).use { c ->
                val bitmap=BitmapFactory.decodeFile(fixture(photo).path)
                val p=c.classify(bitmap)
                assertEquals(3,p.scores.size)
                assertTrue(p.scores.all { it.isFinite() && it>=0f && it<=1f })
                assertEquals(1f,p.scores.sum(),.0001f)
                assertEquals(Decision.choose(p.scores,.7f),p.selected)
                assertTrue(p.inferenceMs>0)
            }
        }
    }
    @Test fun imageInferenceSwitchAndRecreate() {
        ActivityScenario.launch(MainActivity::class.java).use { s ->
            ready(s)
            s.onActivity { assertFalse(button(it,"Kiểm tra thực phẩm").isEnabled) }
            load(s,fixture("meat.jpg"))
            s.onActivity {
                assertTrue(button(it,"Kiểm tra thực phẩm").isEnabled)
                MainActivity::class.java.getDeclaredMethod("analyzeImage").apply { isAccessible=true }.invoke(it)
            }
            ready(s)
            assertFalse(HistoryStore(context).text().contains("Chưa có lần"))
            s.onActivity { children(it.window.decorView).filterIsInstance<Spinner>().first().setSelection(1) }
            instrumentation.waitForIdleSync();ready(s)
            load(s,fixture("fruit.png"))
            s.onActivity { MainActivity::class.java.getDeclaredMethod("analyzeImage").apply { isAccessible=true }.invoke(it) }
            ready(s)
            s.recreate();ready(s)
            s.onActivity { assertEquals(1,children(it.window.decorView).filterIsInstance<Spinner>().first().selectedItemPosition) }
        }
    }
    @Test fun corruptImageDoesNotReusePreviousPhoto() {
        ActivityScenario.launch(MainActivity::class.java).use { s ->
            ready(s);load(s,fixture("meat.jpg"))
            val f=File(context.cacheDir,"invalid.jpg").apply { writeText("broken image") }
            load(s,f)
            s.onActivity { assertFalse(button(it,"Kiểm tra thực phẩm").isEnabled) }
        }
    }
    @Test fun historyRetentionAndDeletion() {
        val h=HistoryStore(context);h.clear()
        repeat(55) { h.add("sample-$it",Prediction(floatArrayOf(.8f,.1f,.1f),0,1.0,1.0),"test-only") }
        val raw=org.json.JSONArray(context.getSharedPreferences("history",0).getString("items","[]"))
        assertEquals(50,raw.length());assertEquals("sample-54",raw.getJSONObject(0).getString("food"))
        h.clear();assertEquals("Chưa có lần kiểm tra nào.",h.text())
    }
    @Test fun historyExportsCsvWithAllThreeScores() {
        val h=HistoryStore(context);h.clear()
        h.add("quả, mẫu 1",Prediction(floatArrayOf(.8f,.1f,.1f),0,12.3,14.0),"fruit-test")
        val file=h.exportCsv(File(context.cacheDir,"history-test.csv"))
        val rows=file.readLines()
        assertEquals(2,rows.size)
        assertEquals("timestamp_ms,food,result,model_version,inference_ms,fresh_score,suspicious_score,spoiled_score",rows.first())
        assertTrue(rows[1].contains("\"quả, mẫu 1\""));assertTrue(rows[1].contains("fruit-test"))
    }
    @Test fun inputGuardRejectsBadQualityAndStrongOutOfScopeLabels() {
        fun solid(color:Int)=Bitmap.createBitmap(64,64,Bitmap.Config.ARGB_8888).apply { eraseColor(color) }
        assertEquals(GuardIssue.TOO_DARK,InputGuard.quality(solid(Color.BLACK)).issue)
        assertEquals(GuardIssue.TOO_BRIGHT,InputGuard.quality(solid(Color.WHITE)).issue)
        assertEquals(GuardIssue.OUT_OF_SCOPE,InputGuard.semantic(listOf(SemanticLabel("Car",.92f)),true).issue)
        assertEquals(GuardIssue.OUT_OF_SCOPE,InputGuard.semantic(listOf(SemanticLabel("Person",.85f)),false).issue)
        assertNull(InputGuard.semantic(listOf(SemanticLabel("Fruit",.91f),SemanticLabel("Person",.72f)),true).issue)
    }
    @Test fun rotatedJpegAndLargeImageDecode() {
        val f=File(context.cacheDir,"rotate.jpg")
        android.graphics.Bitmap.createBitmap(120,60,android.graphics.Bitmap.Config.ARGB_8888).apply { eraseColor(android.graphics.Color.RED) }.let { b ->
            f.outputStream().use { b.compress(android.graphics.Bitmap.CompressFormat.JPEG,95,it) }
        }
        androidx.exifinterface.media.ExifInterface(f.path).apply {
            setAttribute(androidx.exifinterface.media.ExifInterface.TAG_ORIENTATION,"6");saveAttributes()
        }
        val rotated=Images.load(context,Uri.fromFile(f));assertEquals(60,rotated.width);assertEquals(120,rotated.height)
        val big=File(context.cacheDir,"large.png")
        android.graphics.Bitmap.createBitmap(3200,1600,android.graphics.Bitmap.Config.ARGB_8888).let { b -> big.outputStream().use { b.compress(android.graphics.Bitmap.CompressFormat.PNG,100,it) };b.recycle() }
        val small=Images.load(context,Uri.fromFile(big));assertTrue(maxOf(small.width,small.height)<=1600)
    }
    @Test fun sourcesAndModelLabelsAreExplicit() {
        val source=context.assets.open("research_sources.txt").bufferedReader().use { it.readText() }
        assertTrue(source.contains("KHÔNG phải checkpoint"));assertTrue(source.contains("7224690"))
        for(name in listOf("published_model_config.json","fruit_model_config.json")) {
            val c=org.json.JSONObject(context.assets.open(name).bufferedReader().use { it.readText() })
            assertEquals(Decision.labels,(0..2).map { c.getJSONArray("labels").getString(it) })
        }
    }
    @Test fun benchmarkExports100Rows() {
        val s: ActivityScenario<MainActivity> = ActivityScenario.launch(MainActivity::class.java)
        try {
            ready(s);load(s,fixture("meat.jpg"))
            val export=File(context.cacheDir,"exports/benchmark.csv")
            export.delete()
            s.onActivity { MainActivity::class.java.getDeclaredMethod("runBenchmark").apply { isAccessible=true }.invoke(it) }
            for(i in 0 until 600) {
                if(export.exists() && export.readLines().size==101) break
                SystemClock.sleep(200)
            }
            assertTrue("benchmark.csv was not created",export.exists())
            val rows=export.readLines()
            assertEquals(101,rows.size)
            assertEquals("device,android,model_version,model_sha256,threads,warmups,iteration,inference_ms",rows.first())
            instrumentation.sendKeyDownUpSync(android.view.KeyEvent.KEYCODE_BACK)
        } finally {
            s.close()
        }
    }
    @Test fun missingConfigIsRejected() {
        try { PublishedMeatClassifier(context,"missing.json");fail("Missing model must be rejected") } catch(_: java.io.FileNotFoundException) {}
    }
}
