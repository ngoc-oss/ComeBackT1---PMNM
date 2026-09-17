// SPDX-License-Identifier: MIT
// FreshCheck source is licensed under MIT; see LICENSE at repository root.
package vn.freshcheck.app

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Matrix
import android.net.Uri
import androidx.exifinterface.media.ExifInterface

object Images {
    fun load(context: Context, uri: Uri): Bitmap {
        val bounds = BitmapFactory.Options().apply { inJustDecodeBounds = true }
        context.contentResolver.openInputStream(uri).use { BitmapFactory.decodeStream(it, null, bounds) }
        require(bounds.outWidth > 0 && bounds.outHeight > 0) { "Không đọc được ảnh." }
        var sample = 1
        while (maxOf(bounds.outWidth, bounds.outHeight)/sample > 1600) sample *= 2
        val bitmap = context.contentResolver.openInputStream(uri).use {
            BitmapFactory.decodeStream(it, null, BitmapFactory.Options().apply {
                inSampleSize = sample
                inPreferredConfig = Bitmap.Config.ARGB_8888
            })
        } ?: error("Ảnh không hợp lệ.")
        val orientation = context.contentResolver.openInputStream(uri).use {
            if (it == null) 1 else ExifInterface(it).getAttributeInt(ExifInterface.TAG_ORIENTATION, 1)
        }
        val matrix = Matrix()
        when (orientation) {
            2 -> matrix.setScale(-1f, 1f)
            3 -> matrix.setRotate(180f)
            4 -> matrix.setScale(1f, -1f)
            5 -> { matrix.setRotate(90f); matrix.postScale(-1f, 1f) }
            6 -> matrix.setRotate(90f)
            7 -> { matrix.setRotate(-90f); matrix.postScale(-1f, 1f) }
            8 -> matrix.setRotate(-90f)
        }
        return Bitmap.createBitmap(bitmap, 0, 0, bitmap.width, bitmap.height, matrix, true)
    }
    fun crop(bitmap: Bitmap): Bitmap {
        val side = minOf(bitmap.width, bitmap.height)
        val square = Bitmap.createBitmap(bitmap, (bitmap.width-side)/2, (bitmap.height-side)/2, side, side)
        return Bitmap.createScaledBitmap(square, 224, 224, true)
    }
}
