# Requirements Document: Emergency Care Health Observer (E.C.H.O.)

## Introduction

The Emergency Care Health Observer (E.C.H.O.) is an AI-powered emergency monitoring system designed to detect distress signals in audio input and provide conversational assistance to injured individuals. The system continuously monitors audio for signs of pain or injury, uses machine learning to classify distress sounds, and engages with the person through natural language conversation to assess their condition and provide guidance until care is complete.

## Glossary

- **E.C.H.O.**: Emergency Care Health Observer - the complete system
- **Audio_Monitor**: Component responsible for capturing and analyzing audio input
- **Distress_Detector**: Component that classifies audio and identifies distress signals
- **Conversation_Manager**: Component that manages AI-driven conversations with users
- **Voice_Interface**: Component handling text-to-speech and speech recognition
- **GUI**: Graphical User Interface for system control and status display
- **Distress_Signal**: Audio classified as screaming, crying, moaning, or gasping indicating pain or injury
- **Confidence_Threshold**: Minimum classification confidence (0.0-1.0) required to trigger distress response
- **Volume_Threshold**: Minimum audio amplitude required to trigger analysis
- **CLAP_Model**: LAION CLAP (Contrastive Language-Audio Pretraining) model for zero-shot audio classification
- **LLM**: Large Language Model used for conversational responses (Ollama)

## Requirements

### Requirement 1: Real-Time Audio Monitoring

**User Story:** As a system operator, I want E.C.H.O. to continuously monitor audio input in real-time, so that distress signals can be detected immediately when they occur.

#### Acceptance Criteria

1. WHEN the system is activated, THE Audio_Monitor SHALL capture audio at 48kHz sample rate
2. WHEN audio is captured, THE Audio_Monitor SHALL process audio in 1-second chunks without blocking the user interface
3. WHEN the microphone is disabled, THE Audio_Monitor SHALL pause audio capture and resume when re-enabled
4. WHEN audio volume exceeds the Volume_Threshold, THE Audio_Monitor SHALL trigger audio classification
5. THE Audio_Monitor SHALL operate continuously until the system is deactivated

### Requirement 2: Distress Signal Detection

**User Story:** As a system operator, I want E.C.H.O. to accurately identify distress signals in audio, so that emergency assistance can be provided when someone is injured.

#### Acceptance Criteria

1. WHEN audio volume exceeds the Volume_Threshold, THE Distress_Detector SHALL classify audio using the CLAP_Model with zero-shot classification
2. THE Distress_Detector SHALL classify audio into candidate categories: screaming in pain, crying in agony, moaning in injury, gasping for air, talking, laughter, clapping, normal speech, background noise, and silence
3. WHEN classification confidence exceeds the Confidence_Threshold for any distress category, THE Distress_Detector SHALL trigger the emergency response protocol
4. WHEN audio volume exceeds 0.6 regardless of classification, THE Distress_Detector SHALL trigger the emergency response protocol
5. WHEN audio is classified as non-distress sounds, THE Distress_Detector SHALL continue monitoring without triggering emergency response
6. THE Distress_Detector SHALL return the top classification label and confidence score for each analysis

### Requirement 3: Emergency Response Protocol

**User Story:** As a system operator, I want E.C.H.O. to initiate appropriate emergency response when distress is detected, so that injured individuals receive immediate assistance.

#### Acceptance Criteria

1. WHEN distress is detected, THE Conversation_Manager SHALL initiate a conversation by asking if the person is injured
2. WHEN initiating conversation, THE Conversation_Manager SHALL include the detected distress type in the initial message
3. THE Conversation_Manager SHALL maintain conversation context throughout the interaction
4. WHEN the user indicates care is complete or says "stop", THE Conversation_Manager SHALL terminate the conversation and resume monitoring
5. WHEN the system is deactivated during conversation, THE Conversation_Manager SHALL terminate the conversation gracefully

### Requirement 4: Conversational AI Assistance

**User Story:** As an injured person, I want E.C.H.O. to engage in natural conversation with me, so that I can communicate my condition and receive appropriate guidance.

#### Acceptance Criteria

1. THE Conversation_Manager SHALL use an LLM to generate contextually appropriate responses
2. WHEN generating responses, THE Conversation_Manager SHALL maintain chat history for conversation continuity
3. THE Conversation_Manager SHALL generate responses that are concise and appropriate for emergency situations
4. WHEN the user speaks, THE Conversation_Manager SHALL capture audio for 5 seconds and convert speech to text
5. WHEN speech recognition fails, THE Conversation_Manager SHALL continue listening without error
6. THE Conversation_Manager SHALL recognize termination phrases: "satisfied", "i am good", "care is complete", "stop", "deactivate"

### Requirement 5: Voice Interface

**User Story:** As a user, I want E.C.H.O. to communicate through voice, so that I can interact with the system hands-free during an emergency.

#### Acceptance Criteria

1. THE Voice_Interface SHALL convert text responses to speech using text-to-speech synthesis
2. WHEN generating speech, THE Voice_Interface SHALL use a clear, professional voice (en-US-EricNeural)
3. THE Voice_Interface SHALL play synthesized speech through the system audio output
4. WHEN speech playback completes, THE Voice_Interface SHALL clean up temporary audio files
5. THE Voice_Interface SHALL convert user speech to text using speech recognition
6. WHEN speech recognition encounters network errors, THE Voice_Interface SHALL log the error and continue operation
7. THE Voice_Interface SHALL amplify captured audio by 1.5x to improve recognition accuracy

### Requirement 6: Privacy Controls

**User Story:** As a user, I want to control when the microphone is active, so that I can maintain privacy when the system is not needed.

#### Acceptance Criteria

1. THE GUI SHALL provide a microphone toggle control
2. WHEN the microphone is toggled off, THE Audio_Monitor SHALL stop capturing audio immediately
3. WHEN the microphone is toggled on, THE Audio_Monitor SHALL resume capturing audio immediately
4. THE GUI SHALL display the current microphone state (ON/OFF) clearly
5. WHEN the microphone is disabled during conversation, THE Conversation_Manager SHALL pause conversation

### Requirement 7: System Status Display

**User Story:** As a system operator, I want clear visual feedback of E.C.H.O.'s current state, so that I can understand what the system is doing at any time.

#### Acceptance Criteria

1. THE GUI SHALL display the current system state: INITIALIZING, STANDBY, MONITORING, ANALYZING, DISTRESS DETECTED, LISTENING, or THINKING
2. WHEN the system state is MONITORING, THE GUI SHALL display status in green color
3. WHEN the system state is ANALYZING, THE GUI SHALL display status in yellow color
4. WHEN the system state is DISTRESS DETECTED, THE GUI SHALL display status in red color
5. WHEN the system state is LISTENING or THINKING, THE GUI SHALL display status in blue or magenta color
6. THE GUI SHALL display a subtitle providing additional context for the current state
7. THE GUI SHALL update status display in real-time as system state changes

### Requirement 8: Event Logging

**User Story:** As a system operator, I want comprehensive logs of all system events, so that I can review system activity and troubleshoot issues.

#### Acceptance Criteria

1. THE GUI SHALL maintain a log of all system events, alerts, and conversations
2. THE GUI SHALL categorize log entries as: system events, alerts, AI responses, or user input
3. THE GUI SHALL display logs in a separate window when requested
4. WHEN displaying logs, THE GUI SHALL use color coding: cyan for system, red for alerts, white for AI, gray for user
5. THE GUI SHALL preserve log history throughout the session
6. WHEN new log entries are added, THE GUI SHALL automatically scroll to show the latest entry

### Requirement 9: System Control

**User Story:** As a system operator, I want to start and stop E.C.H.O. monitoring, so that I can control when the system is active.

#### Acceptance Criteria

1. THE GUI SHALL provide an activate/deactivate button for system control
2. WHEN the system is activated, THE Audio_Monitor SHALL begin monitoring and the button SHALL display "DEACTIVATE"
3. WHEN the system is deactivated, THE Audio_Monitor SHALL stop monitoring and the button SHALL display "ACTIVATE SYSTEM"
4. WHEN activation is requested before model loading completes, THE GUI SHALL display a warning message
5. THE GUI SHALL change button color to indicate active state (green for inactive, red for active)

### Requirement 10: Model Initialization

**User Story:** As a system operator, I want E.C.H.O. to load AI models efficiently at startup, so that the system is ready for use quickly.

#### Acceptance Criteria

1. WHEN the application starts, THE Distress_Detector SHALL load the CLAP_Model in a background thread
2. WHILE the model is loading, THE GUI SHALL display "INITIALIZING" status
3. WHEN model loading completes successfully, THE GUI SHALL display "STANDBY" status
4. WHEN model loading fails, THE GUI SHALL display "ERROR" status and log the failure
5. THE Distress_Detector SHALL prevent system activation until model loading completes

### Requirement 11: Error Handling and Resilience

**User Story:** As a system operator, I want E.C.H.O. to handle errors gracefully, so that temporary failures don't crash the system.

#### Acceptance Criteria

1. WHEN audio capture fails, THE Audio_Monitor SHALL log the error and prevent system activation
2. WHEN speech recognition encounters network errors, THE Voice_Interface SHALL log the error and continue operation
3. WHEN speech recognition cannot understand audio, THE Voice_Interface SHALL log a placeholder and continue listening
4. WHEN voice synthesis fails, THE Voice_Interface SHALL log the error and continue operation
5. WHEN the LLM fails to generate a response, THE Conversation_Manager SHALL log the error and continue conversation
6. WHEN temporary audio files cannot be deleted, THE Voice_Interface SHALL ignore the error and continue operation

### Requirement 12: Non-Blocking Operation

**User Story:** As a user, I want the E.C.H.O. interface to remain responsive during audio processing, so that I can control the system at any time.

#### Acceptance Criteria

1. THE Audio_Monitor SHALL execute monitoring logic in a separate thread from the GUI
2. THE GUI SHALL remain responsive to user input while audio processing occurs
3. WHEN the system is deactivated, THE Audio_Monitor SHALL stop processing within 1 second
4. THE GUI SHALL update status displays using thread-safe operations
5. THE GUI SHALL update log displays using thread-safe operations
