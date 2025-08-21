package com.example.empty_activity_template.core

import kotlinx.coroutines.delay

class MockLlmService : LlmService {
    override suspend fun complete(
        role: String,
        systemPrompt: String?,
        userPrompt: String,
        memory: List<String>
    ): String {
        delay(400)
        val memoryNote = if (memory.isNotEmpty()) "\nMEMORY: " + memory.joinToString(" | ") else ""
        return "[$role] Response to: '" + userPrompt.take(60) + "'\n" +
            (systemPrompt?.let { "SYS: $it\n" } ?: "") +
            "CODE:\n" +
            "// generated code sample\n" +
            "fun sample() = \"Hello from $role\"" + memoryNote
    }
}

