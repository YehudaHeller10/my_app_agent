package com.example.empty_activity_template.core

interface LlmService {
    suspend fun complete(
        role: String,
        systemPrompt: String?,
        userPrompt: String,
        memory: List<String>
    ): String
}

