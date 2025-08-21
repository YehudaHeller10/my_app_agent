package com.example.empty_activity_template.ui

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.empty_activity_template.agents.AgentOrchestrator
import com.example.empty_activity_template.core.LlmService
import com.example.empty_activity_template.core.MockLlmService
import com.example.empty_activity_template.model.AgentEvent
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

data class UiState(
    val isRunning: Boolean = false,
    val progressMessage: String = "Idle",
    val messages: List<String> = emptyList()
)

class MainViewModel(app: Application) : AndroidViewModel(app) {
    private val llm: LlmService = MockLlmService()
    private val orchestrator = AgentOrchestrator(app.applicationContext, llm)

    private val _state = MutableStateFlow(UiState())
    val state: StateFlow<UiState> = _state

    fun run(prompt: String) {
        if (_state.value.isRunning || prompt.isBlank()) return
        _state.value = _state.value.copy(isRunning = true, progressMessage = "Starting...", messages = emptyList())

        viewModelScope.launch {
            orchestrator.run(prompt) { event ->
                when (event) {
                    is AgentEvent.Progress -> {
                        _state.value = _state.value.copy(progressMessage = event.message)
                    }
                    is AgentEvent.OutputFile -> {
                        val updated = _state.value.messages + ("Saved: " + event.path)
                        _state.value = _state.value.copy(messages = updated)
                    }
                    is AgentEvent.Done -> {
                        val updated = _state.value.messages + ("Done: " + event.summary)
                        _state.value = _state.value.copy(messages = updated, isRunning = false)
                    }
                    is AgentEvent.Error -> {
                        val updated = _state.value.messages + ("Error: " + event.error)
                        _state.value = _state.value.copy(messages = updated, isRunning = false, progressMessage = "Error")
                    }
                }
            }
        }
    }
}

