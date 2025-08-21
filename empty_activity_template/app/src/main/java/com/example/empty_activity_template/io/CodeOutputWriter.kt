package com.example.empty_activity_template.io

import android.content.Context
import java.io.File

class CodeOutputWriter(private val context: Context) {
    fun write(fileName: String, contents: String): String {
        val dir: File = File(context.filesDir, "generated")
        if (!dir.exists()) dir.mkdirs()
        val file = File(dir, fileName)
        file.writeText(contents)
        return file.absolutePath
    }
}

