// SPDX-License-Identifier: MIT
// FreshCheck source is licensed under MIT; see LICENSE.
package vn.freshcheck.app
import android.graphics.Bitmap

data class Prediction(val scores: FloatArray, val selected: Int?, val inferenceMs: Double, val totalMs: Double)

interface Classifier : AutoCloseable {
    val version: String
    val sha256: String
    val foods: List<String>
    fun classify(bitmap: Bitmap): Prediction
    fun benchmark(bitmap: Bitmap): List<Double>
    fun preview(bitmap: Bitmap): Bitmap
}
