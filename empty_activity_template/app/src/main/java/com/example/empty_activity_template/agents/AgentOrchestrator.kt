package com.example.empty_activity_template.agents

import android.content.Context
import com.example.empty_activity_template.core.LlmService
import com.example.empty_activity_template.model.AgentEvent
import com.example.empty_activity_template.io.CodeOutputWriter

class AgentOrchestrator(
    private val appContext: Context,
    private val llmService: LlmService
) {
    private val memory: MutableList<String> = mutableListOf()

    suspend fun run(prompt: String, onEvent: (AgentEvent) -> Unit) {
        try {
            onEvent(AgentEvent.Progress("Planning..."))
            val plan = llmService.complete(
                role = "PLANNER",
                systemPrompt = "You are a planner. Break down the task.",
                userPrompt = prompt,
                memory = memory.toList()
            )
            memory += plan

            onEvent(AgentEvent.Progress("Coding..."))
            val code = llmService.complete(
                role = "CODER",
                systemPrompt = "You are a coder. Generate concise, runnable code.",
                userPrompt = prompt,
                memory = memory.toList()
            )
            memory += code

            val writer = CodeOutputWriter(appContext)
            val path = writer.write("GeneratedCode.kt", code)
            onEvent(AgentEvent.OutputFile(path))

            onEvent(AgentEvent.Progress("Reviewing..."))
            val review = llmService.complete(
                role = "REVIEWER",
                systemPrompt = "You are a reviewer. Provide brief feedback.",
                userPrompt = prompt,
                memory = memory.toList()
            )
            memory += review

            onEvent(AgentEvent.Done("Completed. Files saved and review ready."))
        } catch (t: Throwable) {
            onEvent(AgentEvent.Error(t.message ?: "Unknown error"))
        }
    }
}

