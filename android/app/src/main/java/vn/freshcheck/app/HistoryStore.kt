// SPDX-License-Identifier: MIT
// FreshCheck source is licensed under MIT; see LICENSE at repository root.
package vn.freshcheck.app

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject
import java.text.DateFormat
import java.io.File
import java.util.Date

class HistoryStore(context: Context) {
    private val prefs = context.getSharedPreferences("history", Context.MODE_PRIVATE)
    private fun all(): JSONArray = runCatching { JSONArray(prefs.getString("items","[]")) }.getOrDefault(JSONArray())
    fun add(food: String, p: Prediction, version: String) {
        val old = all()
        val fresh = JSONArray().put(JSONObject().put("time",System.currentTimeMillis())
            .put("food",food).put("result",Decision.title(p.selected)).put("version",version)
            .put("inference_ms",p.inferenceMs).put("scores",JSONArray(p.scores.toList())))
        for (i in 0 until minOf(old.length(),49)) fresh.put(old.getJSONObject(i))
        prefs.edit().putString("items",fresh.toString()).apply()
    }
    fun text(): String {
        val items = all()
        return if (items.length()==0) "Chưa có lần kiểm tra nào." else
            (0 until items.length()).joinToString("\n\n") {
                val r = items.getJSONObject(it)
                "${r.getString("result")} · ${r.getString("food")}\n${DateFormat.getDateTimeInstance().format(Date(r.getLong("time")))} · model ${r.getString("version") }"
            }
    }
    fun clear() { prefs.edit().clear().apply() }
    fun exportCsv(file: File): File {
        file.parentFile?.mkdirs()
        fun quote(value: String) = "\"" + value.replace("\"", "\"\"") + "\""
        val items = all()
        file.bufferedWriter().use { writer ->
            writer.write("timestamp_ms,food,result,model_version,inference_ms,fresh_score,suspicious_score,spoiled_score\n")
            for (i in 0 until items.length()) {
                val row = items.getJSONObject(i)
                val scores = row.getJSONArray("scores")
                writer.write("${row.getLong("time")},${quote(row.getString("food"))},${quote(row.getString("result"))},${quote(row.getString("version"))},${row.getDouble("inference_ms")},${scores.getDouble(0)},${scores.getDouble(1)},${scores.getDouble(2)}\n")
            }
        }
        return file
    }
}
