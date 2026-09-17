// SPDX-License-Identifier: MIT
package vn.freshcheck.app

import android.graphics.Bitmap
import java.util.Locale
import kotlin.math.sqrt

enum class GuardIssue { TOO_DARK, TOO_BRIGHT, LOW_CONTRAST, BLURRY, OUT_OF_SCOPE }
data class GuardResult(val issue: GuardIssue? = null, val detail: String = "", val warning: String? = null)
data class SemanticLabel(val text: String, val confidence: Float)

/** Fast pre-inference checks. Thresholds are conservative heuristics, not food-safety tests. */
object InputGuard {
    fun quality(source: Bitmap): GuardResult {
        val scale = minOf(1f, 256f / maxOf(source.width, source.height))
        val width = maxOf(8, (source.width * scale).toInt())
        val height = maxOf(8, (source.height * scale).toInt())
        val bitmap = if (width == source.width && height == source.height) source
        else Bitmap.createScaledBitmap(source, width, height, true)
        val pixels = IntArray(width * height)
        bitmap.getPixels(pixels, 0, width, 0, 0, width, height)
        if (bitmap !== source) bitmap.recycle()
        val gray = DoubleArray(pixels.size)
        var sum = 0.0
        pixels.forEachIndexed { i, p ->
            val y = (0.2126 * ((p shr 16) and 255) + 0.7152 * ((p shr 8) and 255) + 0.0722 * (p and 255))
            gray[i] = y; sum += y
        }
        val mean = sum / gray.size
        val deviation = sqrt(gray.sumOf { (it - mean) * (it - mean) } / gray.size)
        var lapSum = 0.0; var lapSq = 0.0; var count = 0
        for (y in 1 until height - 1) for (x in 1 until width - 1) {
            val i = y * width + x
            val lap = 4 * gray[i] - gray[i - 1] - gray[i + 1] - gray[i - width] - gray[i + width]
            lapSum += lap; lapSq += lap * lap; count++
        }
        val lapVariance = if (count == 0) 0.0 else lapSq / count - (lapSum / count) * (lapSum / count)
        val detail = String.format(Locale.US, "sáng %.1f/255 · tương phản %.1f · nét %.1f", mean, deviation, lapVariance)
        return when {
            mean < 25 -> GuardResult(GuardIssue.TOO_DARK, detail)
            mean > 235 -> GuardResult(GuardIssue.TOO_BRIGHT, detail)
            deviation < 8 -> GuardResult(GuardIssue.LOW_CONTRAST, detail)
            lapVariance < 35 -> GuardResult(GuardIssue.BLURRY, detail)
            mean < 40 || mean > 220 || lapVariance < 70 -> GuardResult(detail = detail, warning = detail)
            else -> GuardResult(detail = detail)
        }
    }

    fun semantic(labels: List<SemanticLabel>, fruitMode: Boolean): GuardResult {
        val negative = setOf("person", "people", "human", "face", "car", "vehicle", "bus", "train", "airplane",
            "bicycle", "motorcycle", "furniture", "computer", "mobile phone", "electronics", "building", "dog", "cat")
        val commonFood = setOf("food", "produce", "ingredient", "cuisine", "dish", "fruit", "vegetable", "meat")
        val domain = if (fruitMode)
            setOf("apple", "banana", "orange", "mango", "guava", "lime", "lemon", "pear", "peach", "grape", "papaya", "pineapple")
        else setOf("beef", "steak", "pork", "lamb", "veal", "mutton", "red meat", "raw meat")
        fun best(words: Set<String>) = labels.filter { label -> words.any { w -> label.text.lowercase(Locale.US).contains(w) } }
            .maxOfOrNull { it.confidence } ?: 0f
        val bad = best(negative)
        val good = maxOf(best(commonFood), best(domain))
        return if (bad >= .70f && bad > good + .10f) {
            val label = labels.maxByOrNull { if (negative.any { n -> it.text.lowercase(Locale.US).contains(n) }) it.confidence else -1f }
            GuardResult(GuardIssue.OUT_OF_SCOPE, "${label?.text ?: "object"} ${String.format(Locale.US, "%.0f%%", bad * 100)}")
        } else if (good < .45f) {
            GuardResult(warning = "Bộ lọc chưa xác nhận chắc chắn đây là thực phẩm; hãy tự kiểm tra phạm vi ảnh.")
        } else GuardResult()
    }
}
