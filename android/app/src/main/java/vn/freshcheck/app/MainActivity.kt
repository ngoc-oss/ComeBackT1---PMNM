// SPDX-License-Identifier: MIT
// FreshCheck source is licensed under MIT; see LICENSE at repository root.
package vn.freshcheck.app

import android.app.AlertDialog
import android.content.Intent
import android.content.res.ColorStateList
import android.graphics.Bitmap
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.SystemClock
import android.view.Gravity
import android.view.View
import android.widget.*
import androidx.activity.ComponentActivity
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.FileProvider
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.label.ImageLabeling
import com.google.mlkit.vision.label.defaults.ImageLabelerOptions
import java.io.File
import java.util.Locale
import java.util.concurrent.Executors
import kotlin.math.ceil

class MainActivity : ComponentActivity() {
    private val worker = Executors.newSingleThreadExecutor()
    private var classifier: Classifier? = null
    private var bitmap: Bitmap? = null
    private var pendingUri: Uri? = null
    private var deferredImage: Uri? = null
    private var busy = true
    private lateinit var status: TextView
    private lateinit var result: TextView
    private lateinit var timing: TextView
    private lateinit var modelInfo: TextView
    private lateinit var image: ImageView
    private lateinit var spinner: Spinner
    private lateinit var domain: Spinner
    private var fruitMode = false
    private lateinit var analyze: Button
    private lateinit var benchmark: Button
    private lateinit var capture: Button
    private lateinit var gallery: Button
    private lateinit var retake: Button
    private lateinit var progress: ProgressBar
    private lateinit var history: HistoryStore
    private lateinit var scroll: ScrollView
    private lateinit var verdictPanel: LinearLayout
    private lateinit var bars: List<ProgressBar>
    private lateinit var scoreLabels: List<TextView>
    private val green = Color.rgb(20,125,100)
    private val ink = Color.rgb(22,48,44)
    private val labeler by lazy {
        ImageLabeling.getClient(ImageLabelerOptions.Builder().setConfidenceThreshold(.45f).build())
    }

    private val takePhoto = registerForActivityResult(ActivityResultContracts.TakePicture()) { ok ->
        if (ok) pendingUri?.let { loadImage(it) }
    }
    private val pickPhoto = registerForActivityResult(ActivityResultContracts.GetContent()) { uri ->
        uri?.let { loadImage(it) }
    }
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        pendingUri = savedInstanceState?.getString("pending_uri")?.let(Uri::parse)
        fruitMode = savedInstanceState?.getBoolean("fruit_mode") ?: false
        history = HistoryStore(this)
        buildUi()
        loadClassifier()
    }
    private fun loadClassifier() {
        setBusy(true)
        worker.execute {
            classifier?.close()
            classifier = null
            val loaded = runCatching<Classifier> {
                if(fruitMode) PublishedMeatClassifier(applicationContext, "fruit_model_config.json")
                else PublishedMeatClassifier(applicationContext)
            }
            classifier = loaded.getOrNull()
            runOnUiThread {
                if (!isDestroyed) {
                    loaded.onSuccess { c ->
                        spinner.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, c.foods)
                        status.text = getString(if(fruitMode) R.string.ready_fruit else R.string.ready_meat)
                        modelInfo.text = getString(R.string.model_info_format, c.version, c.sha256.take(12))
                        bitmap?.let { image.setImageBitmap(c.preview(it)) }
                        result.text = getString(if(bitmap == null) R.string.ready_no_image else R.string.image_ready_new_model)
                        timing.text = getString(R.string.choose_image)
                        bars.forEach { it.progress = 0 }
                        scoreLabels.forEachIndexed { i,t -> t.text = Decision.title(i) }
                    }.onFailure {
                        status.text = getString(R.string.model_load_error, it.message ?: "")
                    }
                    setBusy(false)
                    deferredImage?.let { uri -> deferredImage = null; loadImage(uri) }
                }
            }
        }
    }
    override fun onSaveInstanceState(outState: Bundle) {
        outState.putString("pending_uri",pendingUri?.toString())
        outState.putBoolean("fruit_mode",fruitMode)
        super.onSaveInstanceState(outState)
    }
    override fun onDestroy() {
        labeler.close()
        worker.execute { classifier?.close() }
        worker.shutdown()
        super.onDestroy()
    }
    private fun dp(n: Int) = (n*resources.displayMetrics.density).toInt()
    private fun text(value: String, size: Float = 16f, bold: Boolean = false) = TextView(this).apply {
        text = value; textSize = size; setTextColor(ink)
        if (bold) setTypeface(typeface, Typeface.BOLD)
        setPadding(0,dp(6),0,dp(6))
    }
    private fun button(value: String, action: () -> Unit) = Button(this).apply {
        text = value; isAllCaps = false; minHeight = dp(52)
        background = GradientDrawable().apply { setColor(green); cornerRadius = dp(16).toFloat() }
        layoutParams = LinearLayout.LayoutParams(-1,-2).apply { topMargin = dp(8); bottomMargin = dp(4) }
        setPadding(dp(16),dp(12),dp(16),dp(12)); elevation = 0f
        setTextColor(Color.WHITE); setOnClickListener { action() }
    }
    private fun panel() = LinearLayout(this).apply {
        orientation = LinearLayout.VERTICAL; setPadding(dp(18),dp(14),dp(18),dp(14))
        background = GradientDrawable().apply { setColor(Color.WHITE); cornerRadius = dp(20).toFloat() }
        layoutParams = LinearLayout.LayoutParams(-1,-2).apply { bottomMargin = dp(16) }
    }
    private fun buildUi() {
        scroll = ScrollView(this).apply { setBackgroundColor(Color.rgb(245,247,242)); isFillViewport = true }
        val body = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL; setPadding(dp(16),dp(14),dp(16),dp(24)) }
        scroll.addView(body)
        setContentView(scroll)
        ViewCompat.setOnApplyWindowInsetsListener(scroll) { view, insets ->
            val b = insets.getInsets(WindowInsetsCompat.Type.systemBars())
            view.setPadding(b.left,b.top,b.right,b.bottom); insets
        }
        val brand = LinearLayout(this).apply { gravity = Gravity.CENTER_VERTICAL }
        brand.addView(ImageView(this).apply { setImageResource(R.drawable.ic_leaf); contentDescription = null },LinearLayout.LayoutParams(dp(36),dp(36)))
        brand.addView(text("  ${getString(R.string.app_name)}",22f,true),LinearLayout.LayoutParams(0,-2,1f))
        brand.addView(text(getString(R.string.offline),11f,true).apply { setTextColor(green) })
        body.addView(brand)
        val hero = panel().apply {
            background = GradientDrawable(GradientDrawable.Orientation.TL_BR,intArrayOf(Color.rgb(17,66,51),Color.rgb(30,107,78))).apply { cornerRadius = dp(24).toFloat() }
            setPadding(dp(22),dp(20),dp(22),dp(20))
        }
        hero.addView(text(getString(R.string.hero_kicker),11f,true).apply { setTextColor(Color.rgb(187,224,174)); letterSpacing = .1f })
        hero.addView(text(getString(R.string.hero_title),28f,true).apply { setTextColor(Color.WHITE) })
        hero.addView(text(getString(R.string.hero_body),14f).apply { setTextColor(Color.rgb(220,236,224)) })
        body.addView(hero)
        status = text(getString(R.string.model_loading),13f).apply { setTextColor(green) }
        body.addView(status)
        modelInfo = text("ONNX Runtime",12f)
        body.addView(modelInfo)
        val photo = panel()
        photo.addView(text(getString(R.string.section_photo),18f,true))
        domain = Spinner(this)
        domain.contentDescription = getString(R.string.domain_description)
        val domains = if(assets.list("")?.contains("fruit_model_config.json")==true) listOf(getString(R.string.domain_meat), getString(R.string.domain_fruit)) else listOf(getString(R.string.domain_meat_source))
        domain.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item, domains)
        domain.onItemSelectedListener = object : AdapterView.OnItemSelectedListener {
            override fun onNothingSelected(parent: AdapterView<*>?) {}
            override fun onItemSelected(parent: AdapterView<*>?, view: View?, position: Int, id: Long) {
                val requested = position == 1
                if(!busy && requested != fruitMode) { fruitMode = requested; loadClassifier() }
            }
        }
        domain.setSelection(if(fruitMode) 1 else 0)
        domain.minimumHeight = dp(48)
        photo.addView(domain)
        spinner = Spinner(this)
        spinner.contentDescription = getString(R.string.food_description)
        spinner.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item,listOf(getString(R.string.model_wait)))
        spinner.minimumHeight = dp(48)
        // One model currently covers one food domain. Keep this selector internal
        // until multiple food types exist, which avoids a misleading duplicate
        // control on compact devices such as the Galaxy A10s.
        spinner.visibility = View.GONE
        photo.addView(spinner)
        photo.addView(text(getString(R.string.photo_hint),14f))
        image = ImageView(this).apply {
            setImageResource(R.drawable.ic_leaf); scaleType = ImageView.ScaleType.FIT_CENTER
            contentDescription = getString(R.string.image_description)
            background = GradientDrawable().apply { setColor(Color.rgb(234,240,227)); cornerRadius = dp(18).toFloat() }
            clipToOutline = true
        }
        photo.addView(image,LinearLayout.LayoutParams(-1,dp(150)))
        capture = button(getString(R.string.capture)) { openCamera() }
        gallery = button(getString(R.string.gallery)) { runCatching { pickPhoto.launch("image/*") }.onFailure { errorDialog(it.message ?: "Không mở được thư viện") } }
        gallery.background = GradientDrawable().apply { setColor(Color.rgb(234,240,227)); cornerRadius = dp(16).toFloat() }
        gallery.setTextColor(ink)
        val photoActions = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL; weightSum = 2f }
        capture.layoutParams = LinearLayout.LayoutParams(0,-2,1f).apply { marginEnd = dp(6) }
        gallery.layoutParams = LinearLayout.LayoutParams(0,-2,1f).apply { marginStart = dp(6) }
        photoActions.addView(capture); photoActions.addView(gallery)
        photo.addView(photoActions)
        body.addView(photo)
        val verdict = panel()
        verdictPanel = verdict
        verdict.addView(text(getString(R.string.section_result),18f,true))
        result = text(getString(R.string.ready_no_image),23f,true)
        verdict.addView(result)
        scoreLabels = List(3) { text(Decision.title(it),14f) }
        bars = List(3) { ProgressBar(this,null,android.R.attr.progressBarStyleHorizontal).apply {
            max = 1000; progressTintList = ColorStateList.valueOf(listOf(green,Color.rgb(180,122,20),Color.rgb(187,64,55))[it])
        } }
        for (i in 0..2) { verdict.addView(scoreLabels[i]); verdict.addView(bars[i]) }
        timing = text(getString(R.string.score_warning),13f)
        verdict.addView(timing)
        progress = ProgressBar(this)
        verdict.addView(progress)
        analyze = button(getString(R.string.analyze)) { confirmAnalyze() }
        verdict.addView(analyze)
        retake = button(getString(R.string.retake)) { openCamera() }.apply {
            background = GradientDrawable().apply { setColor(Color.rgb(234,240,227)); cornerRadius = dp(16).toFloat() }
            setTextColor(ink)
        }
        verdict.addView(retake)
        verdict.addView(text(getString(R.string.filter_note),12f))
        verdict.addView(text(getString(R.string.safety_warning),13f))
        body.addView(verdict)
        val actions = panel()
        actions.addView(button(getString(R.string.history)) {
            AlertDialog.Builder(this).setTitle(getString(R.string.history_title)).setMessage(history.text())
                .setPositiveButton(getString(R.string.close),null)
                .setNeutralButton(getString(R.string.export_history)) { _,_ -> exportHistory() }
                .setNegativeButton(getString(R.string.delete_history)) { _,_ ->
                    AlertDialog.Builder(this).setMessage(getString(R.string.delete_history_question))
                        .setPositiveButton(getString(R.string.delete)) { _,_ -> history.clear() }.setNegativeButton(getString(R.string.cancel),null).show()
                }.show()
        })
        benchmark = button(getString(R.string.benchmark)) { runBenchmark() }
        actions.addView(benchmark)
        actions.addView(button(getString(R.string.sources)) { showSources() })
        actions.addView(text(getString(R.string.privacy_note),13f))
        body.addView(actions)
        setBusy(true)
    }
    private fun setBusy(value: Boolean) {
        busy = value
        progress.visibility = if(value) View.VISIBLE else View.GONE
        capture.isEnabled = !value; gallery.isEnabled = !value
        retake.isEnabled = !value
        domain.isEnabled = !value
        spinner.isEnabled = !value && classifier != null
        analyze.isEnabled = !value && classifier != null && bitmap != null
        benchmark.isEnabled = analyze.isEnabled
    }
    private fun openCamera() {
        runCatching {
            val directory = File(cacheDir,"captures").apply { mkdirs() }
            val file = File(directory,"capture-${System.currentTimeMillis()}.jpg")
            pendingUri = FileProvider.getUriForFile(this,"$packageName.files",file)
            takePhoto.launch(pendingUri!!)
        }.onFailure { errorDialog(getString(R.string.camera_error, it.message ?: "")) }
    }
    private fun loadImage(uri: Uri) {
        if(busy) { deferredImage = uri; return }
        setBusy(true)
        worker.execute {
            val loaded = runCatching { Images.load(applicationContext,uri) }
            runOnUiThread {
                if(!isDestroyed) {
                    loaded.onSuccess {
                        bitmap = it; image.setImageBitmap(classifier?.preview(it) ?: Images.crop(it))
                        result.text = getString(R.string.image_ready); result.setTextColor(ink)
                        bars.forEach { b -> b.progress = 0 }
                        scoreLabels.forEachIndexed { i,t -> t.text = Decision.title(i) }
                        timing.text = getString(R.string.tap_analyze)
                        scroll.post { scroll.smoothScrollTo(0,verdictPanel.top) }
                    }.onFailure { bitmap = null; image.setImageResource(R.drawable.ic_leaf); result.text = getString(R.string.image_invalid); bars.forEach { b -> b.progress = 0 }; scoreLabels.forEachIndexed { i,t -> t.text = Decision.title(i) }; errorDialog(it.message ?: "Không đọc được ảnh") }
                    setBusy(false)
                }
            }
        }
    }
    private fun confirmAnalyze() {
        AlertDialog.Builder(this).setTitle(getString(R.string.confirm_title))
            .setMessage("Ảnh chỉ có ${spinner.selectedItem}, rõ nét? NGHI NGỜ tương ứng mức ${if(fruitMode) "Mild của FruQ-DB" else "Half-Fresh của bộ thịt"}. ${if(fruitMode) "Model quả chưa kiểm định trên tập ảnh điện thoại độc lập." else ""} Bộ lọc phạm vi và chất lượng sẽ chạy trước model; đây không phải kiểm nghiệm an toàn.")
            .setPositiveButton(getString(R.string.confirm_action)) { _,_ -> screenAndAnalyze() }.setNegativeButton(getString(R.string.choose_again),null).show()
    }
    private fun screenAndAnalyze() {
        val current = bitmap ?: return
        val quality = InputGuard.quality(current)
        if (quality.issue != null) { showGuard(quality); return }
        setBusy(true)
        labeler.process(InputImage.fromBitmap(current, 0))
            .addOnSuccessListener { output ->
                if (isDestroyed) return@addOnSuccessListener
                val semantic = InputGuard.semantic(output.map { SemanticLabel(it.text, it.confidence) }, fruitMode)
                if (semantic.issue != null) { setBusy(false); showGuard(semantic) }
                else analyzeImage(listOfNotNull(quality.warning, semantic.warning).joinToString("\n").ifBlank { null })
            }
            .addOnFailureListener {
                if (!isDestroyed) { setBusy(false); errorDialog(getString(R.string.guard_failed)) }
            }
    }
    private fun showGuard(result: GuardResult) {
        val message = when(result.issue) {
            GuardIssue.TOO_DARK -> getString(R.string.guard_dark)
            GuardIssue.TOO_BRIGHT -> getString(R.string.guard_bright)
            GuardIssue.LOW_CONTRAST -> getString(R.string.guard_contrast)
            GuardIssue.BLURRY -> getString(R.string.guard_blurry)
            GuardIssue.OUT_OF_SCOPE -> getString(R.string.guard_scope)
            null -> return
        }
        this.result.text = getString(R.string.guard_result)
        this.result.setTextColor(Color.rgb(174,44,44))
        timing.text = "$message\n${result.detail}"
        AlertDialog.Builder(this).setTitle(getString(R.string.guard_title)).setMessage("$message\n\n${result.detail}")
            .setPositiveButton(getString(R.string.retake)) { _,_ -> openCamera() }.setNegativeButton(getString(R.string.close),null).show()
    }
    @JvmOverloads
    private fun analyzeImage(guardNote: String? = null) {
        val current = bitmap ?: return
        val food = spinner.selectedItem.toString()
        setBusy(true)
        val start = SystemClock.elapsedRealtimeNanos()
        worker.execute {
            val predicted = runCatching { classifier!!.classify(current) }
            runOnUiThread {
                if(!isDestroyed) {
                    predicted.onSuccess { p ->
                        result.text = Decision.title(p.selected)
                        result.setTextColor(when(p.selected) {0 -> green; 2 -> Color.rgb(174,44,44); else -> Color.rgb(142,94,15)})
                        for(i in 0..2) {
                            bars[i].progress = (p.scores[i]*1000).toInt().coerceIn(0,1000)
                            scoreLabels[i].text = "${Decision.title(i)} · ${String.format(Locale.US,"%.1f",p.scores[i]*100)}% điểm mô hình"
                        }
                        val visible = (SystemClock.elapsedRealtimeNanos()-start)/1e6
                        timing.text = String.format(Locale.US,"Model %s · ONNX Runtime\nInference %.1f ms · xử lý %.1f ms · đến UI %.1f ms\n%s%s",classifier!!.version,p.inferenceMs,p.totalMs,visible,
                            if(p.selected==null) "Điểm thấp: hãy chụp lại. Đây không phải nhãn NGHI NGỜ." else "Chỉ là đánh giá dấu hiệu bên ngoài.",
                            guardNote?.let { "\nCảnh báo đầu vào: $it" } ?: "")
                        history.add(food,p,classifier!!.version)
                        scroll.post { scroll.smoothScrollTo(0,verdictPanel.top) }
                    }.onFailure { errorDialog(it.message ?: "Suy luận thất bại") }
                    setBusy(false)
                }
            }
        }
    }
    private fun exportHistory() {
        runCatching { history.exportCsv(File(File(cacheDir,"exports"),"freshcheck-history.csv")) }
            .onSuccess { shareCsv(it, getString(R.string.history_export_title)) }
            .onFailure { errorDialog(it.message ?: getString(R.string.history_export_error)) }
    }
    private fun shareCsv(file: File, title: String) {
        val uri = FileProvider.getUriForFile(this,"$packageName.files",file)
        runCatching { startActivity(Intent.createChooser(Intent(Intent.ACTION_SEND).apply {
            type = "text/csv"; putExtra(Intent.EXTRA_STREAM,uri); addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        },title)) }.onFailure { errorDialog(getString(R.string.history_export_error)) }
    }
    private fun runBenchmark() {
        val current = bitmap ?: return
        setBusy(true)
        worker.execute {
            val measured = runCatching {
                val c = classifier!!
                val values = c.benchmark(current)
                val sorted = values.sorted()
                val file = File(File(cacheDir,"exports").apply { mkdirs() },"benchmark.csv")
                fun quote(s: String) = "\""+s.replace("\"","\"\"")+"\""
                file.bufferedWriter().use { w ->
                    w.write("device,android,model_version,model_sha256,threads,warmups,iteration,inference_ms\n")
                    values.forEachIndexed { i,t ->
                        w.write("${quote(Build.MANUFACTURER+" "+Build.MODEL)},${Build.VERSION.SDK_INT},${quote(c.version)},${c.sha256},4,10,${i+1},${String.format(Locale.US,"%.6f",t)}\n")
                    }
                }
                Triple(file,sorted[ceil(.50*sorted.size).toInt()-1],sorted[ceil(.95*sorted.size).toInt()-1])
            }
            runOnUiThread {
                if(!isDestroyed) {
                    measured.onSuccess { (file,p50,p95) ->
                        timing.text = String.format(Locale.US,"100 lần · 10 warmup\np50 %.1f ms · p95 %.1f ms\nChỉ đo inference cùng một ảnh, không gồm camera/giải mã.",p50,p95)
                        shareCsv(file,"Xuất benchmark")
                    }.onFailure { errorDialog(it.message ?: "Không đo được tốc độ") }
                    setBusy(false)
                }
            }
        }
    }
    private fun showSources() {
        val content = TextView(this).apply {
            text = assets.open("research_sources.txt").bufferedReader().use { it.readText() }
            textSize = 15f; setTextColor(ink); setPadding(dp(20),dp(12),dp(20),dp(12))
            autoLinkMask = android.text.util.Linkify.WEB_URLS
            movementMethod = android.text.method.LinkMovementMethod.getInstance()
        }
        AlertDialog.Builder(this).setTitle(getString(R.string.source_title))
            .setView(ScrollView(this).apply { addView(content) }).setPositiveButton(getString(R.string.close),null).show()
    }
    private fun errorDialog(message: String) {
        AlertDialog.Builder(this).setTitle(getString(R.string.error_title)).setMessage(message).setPositiveButton(getString(R.string.close),null).show()
    }
}
