package com.example.empty_activity_template.model

sealed class AgentEvent {
    data class Progress(val message: String) : AgentEvent()
    data class OutputFile(val path: String) : AgentEvent()
    data class Done(val summary: String) : AgentEvent()
    data class Error(val error: String) : AgentEvent()
}

