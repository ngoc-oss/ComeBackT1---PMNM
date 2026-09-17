// SPDX-License-Identifier: MIT
// FreshCheck source is licensed under MIT; see LICENSE at repository root.
package vn.freshcheck.app

object Decision {
    val labels = listOf("fresh", "suspicious", "spoiled")
    fun choose(scores: FloatArray, threshold: Float): Int? {
        require(scores.size == 3 && scores.all { it.isFinite() })
        require(threshold in 0f..1f)
        val index = scores.indices.maxByOrNull { scores[it] }!!
        return if (scores[index] >= threshold) index else null
    }
    fun title(index: Int?): String = when(index) {
        0 -> "TƯƠI"
        1 -> "NGHI NGỜ"
        2 -> "HƯ"
        else -> "CHƯA ĐỦ CƠ SỞ"
    }
}
