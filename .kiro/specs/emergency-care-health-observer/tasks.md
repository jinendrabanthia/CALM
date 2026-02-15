# Implementation Plan: Emergency Care Health Observer (E.C.H.O.)

## Overview

This implementation plan refactors the existing monolithic E.C.H.O. system into a well-structured, testable architecture with clear separation of concerns. The approach focuses on extracting components from the existing code, adding proper interfaces, implementing comprehensive testing, and ensuring all correctness properties are validated.

## Tasks

- [ ] 1. Set up project structure and testing framework
  - Create modular directory structure separating components
  - Set up Hypothesis for property-based testing
  - Configure pytest with coverage reporting
  - Create shared test fixtures and generators
  - _Requirements: 12.1_

- [ ] 2. Extract and refactor Audio Monitor component
  - [ ] 2.1 Create AudioMonitor class with clean interface
    - Extract audio capture logic from existing code
    - Implement start_monitoring, stop_monitoring, pause_capture, resume_capture methods
    - Add callback mechanism for volume threshold events
    - Use threading.Event for clean shutdown
    - _Requirements: 1.1, 1.2, 1.3, 1.5, 12.1, 12.3_
  
  - [ ]* 2.2 Write property test for volume threshold triggering
    - **Property 1: Volume threshold triggers classification**
    - **Validates: Requirements 1.4**
  
  - [ ]* 2.3 Write property test for microphone state control
    - **Property 2: Microphone state controls audio capture**
    - **Validates: Requirements 1.3, 6.2, 6.3**
  
  - [ ]* 2.4 Write unit tests for Audio Monitor
    - Test 48kHz sample rate configuration
    - Test 1-second chunk size
    - Test clean shutdown within 1 second
    - Test audio capture failure handling
    - _Requirements: 1.1, 1.2, 11.1, 12.3_

- [ ] 3. Extract and refactor Distress Detector component
  - [ ] 3.1 Create DistressDetector class with clean interface
    - Extract classification logic from existing code
    - Implement load_model, classify_audio, is_distress methods
    - Define ClassificationResult data class
    - Add proper error handling for model loading
    - _Requirements: 2.1, 2.2, 2.6, 10.1, 10.4_
  
  - [ ]* 3.2 Write property test for high confidence distress detection
    - **Property 3: High confidence distress triggers emergency response**
    - **Validates: Requirements 2.3**
  
  - [ ]* 3.3 Write property test for high volume detection
    - **Property 4: High volume triggers emergency response**
    - **Validates: Requirements 2.4**
  
  - [ ]* 3.4 Write property test for non-distress classification
    - **Property 5: Non-distress classification continues monitoring**
    - **Validates: Requirements 2.5**
  
  - [ ]* 3.5 Write property test for classification result structure
    - **Property 6: Classification returns structured result**
    - **Validates: Requirements 2.6**
  
  - [ ]* 3.6 Write unit tests for Distress Detector
    - Test candidate labels configuration
    - Test confidence threshold (0.50)
    - Test model loading success and failure
    - Test classification with mocked model
    - _Requirements: 2.2, 10.2, 10.3, 10.4, 10.5_

- [ ] 4. Checkpoint - Ensure core detection tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Extract and refactor Voice Interface component
  - [ ] 5.1 Create VoiceInterface class with clean interface
    - Extract TTS and speech recognition logic
    - Implement speak, listen, set_recognizer_sensitivity methods
    - Add proper error handling for network failures
    - Implement temporary file cleanup
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_
  
  - [ ]* 5.2 Write property test for temporary file cleanup
    - **Property 11: Temporary files cleaned after speech**
    - **Validates: Requirements 5.4**
  
  - [ ]* 5.3 Write property test for audio amplification
    - **Property 12: Audio amplification is consistent**
    - **Validates: Requirements 5.7**
  
  - [ ]* 5.4 Write property test for network error handling
    - **Property 13: Network errors don't crash voice interface**
    - **Validates: Requirements 5.6**
  
  - [ ]* 5.5 Write unit tests for Voice Interface
    - Test en-US-EricNeural voice configuration
    - Test 5-second listen duration
    - Test speech recognition with mocked API
    - Test TTS with mocked edge-tts
    - Test audio playback with mocked pygame
    - _Requirements: 5.2, 5.5_

- [ ] 6. Extract and refactor Conversation Manager component
  - [ ] 6.1 Create ConversationManager class with clean interface
    - Extract conversation logic from existing code
    - Implement start_conversation, stop_conversation, should_terminate methods
    - Define ChatMessage data class
    - Add proper integration with VoiceInterface
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 4.4, 4.6_
  
  - [ ]* 6.2 Write property test for distress type in initial message
    - **Property 7: Initial message includes distress type**
    - **Validates: Requirements 3.2**
  
  - [ ]* 6.3 Write property test for chat history accumulation
    - **Property 8: Chat history accumulates messages**
    - **Validates: Requirements 3.3, 4.2**
  
  - [ ]* 6.4 Write property test for termination phrases
    - **Property 9: Termination phrases end conversation**
    - **Validates: Requirements 3.4, 4.6**
  
  - [ ]* 6.5 Write property test for speech recognition failure handling
    - **Property 10: Speech recognition failures don't crash system**
    - **Validates: Requirements 4.5**
  
  - [ ]* 6.6 Write unit tests for Conversation Manager
    - Test all termination phrases recognized
    - Test conversation initiation with mocked Ollama
    - Test system deactivation during conversation (edge case)
    - Test microphone disabled during conversation (edge case)
    - _Requirements: 3.5, 4.6, 6.5_

- [ ] 7. Checkpoint - Ensure conversation tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Extract and refactor GUI component
  - [ ] 8.1 Create EchoGUI class with clean interface
    - Extract GUI logic from existing code
    - Implement set_status, log, open_log_window methods
    - Separate UI layout from business logic
    - Add thread-safe update mechanisms using root.after()
    - _Requirements: 6.1, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 8.1, 8.2, 8.3, 9.1, 12.4, 12.5_
  
  - [ ]* 8.2 Write property test for microphone state display
    - **Property 14: Microphone state reflected in display**
    - **Validates: Requirements 6.4**
  
  - [ ]* 8.3 Write property test for valid status states
    - **Property 15: Status display shows valid states**
    - **Validates: Requirements 7.1**
  
  - [ ]* 8.4 Write property test for status subtitles
    - **Property 16: Status has subtitle context**
    - **Validates: Requirements 7.6**
  
  - [ ]* 8.5 Write property test for log entry categorization
    - **Property 17: Log entries are categorized**
    - **Validates: Requirements 8.2**
  
  - [ ]* 8.6 Write property test for log color coding
    - **Property 18: Log category determines color**
    - **Validates: Requirements 8.4**
  
  - [ ]* 8.7 Write property test for log accumulation
    - **Property 19: Logs accumulate throughout session**
    - **Validates: Requirements 8.1, 8.5**
  
  - [ ]* 8.8 Write property test for log auto-scroll
    - **Property 20: Log window auto-scrolls to latest**
    - **Validates: Requirements 8.6**
  
  - [ ]* 8.9 Write property test for activation button text
    - **Property 21: Activation button reflects system state**
    - **Validates: Requirements 9.2, 9.3**
  
  - [ ]* 8.10 Write property test for button color state
    - **Property 22: Button color indicates active state**
    - **Validates: Requirements 9.5**
  
  - [ ]* 8.11 Write unit tests for GUI
    - Test all status color mappings (green, yellow, red, cyan, magenta, gray)
    - Test log window creation
    - Test activation before model loads (edge case)
    - Test thread-safe update mechanisms
    - _Requirements: 7.2, 7.3, 7.4, 7.5, 8.3, 9.4, 12.4, 12.5_

- [ ] 9. Implement error handling properties
  - [ ] 9.1 Add comprehensive error handling to all components
    - Implement error logging in AudioMonitor
    - Implement error logging in DistressDetector
    - Implement error logging in VoiceInterface
    - Implement error logging in ConversationManager
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6_
  
  - [ ]* 9.2 Write property test for model loading failure
    - **Property 23: Model loading failure sets error state**
    - **Validates: Requirements 10.4**
  
  - [ ]* 9.3 Write property test for graceful error handling
    - **Property 24: Component errors are logged and handled gracefully**
    - **Validates: Requirements 11.1, 11.2, 11.3, 11.4, 11.5, 11.6**
  
  - [ ]* 9.4 Write unit tests for error scenarios
    - Test audio capture failure
    - Test speech recognition network error
    - Test unrecognized speech handling
    - Test TTS failure
    - Test Ollama failure
    - Test file deletion failure
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6_

- [ ] 10. Implement threading property
  - [ ]* 10.1 Write property test for shutdown timing
    - **Property 25: System stops within timeout**
    - **Validates: Requirements 12.3**
  
  - [ ]* 10.2 Write unit tests for threading
    - Test monitoring runs in separate thread
    - Test GUI remains responsive (integration test)
    - _Requirements: 12.1, 12.2_

- [ ] 11. Create main application orchestrator
  - [ ] 11.1 Implement main application class
    - Wire together all components
    - Implement system activation/deactivation flow
    - Implement main monitoring loop
    - Connect AudioMonitor → DistressDetector → ConversationManager flow
    - _Requirements: 1.5, 3.1, 9.2, 9.3_
  
  - [ ]* 11.2 Write integration tests
    - Test end-to-end distress detection flow
    - Test conversation flow from detection to termination
    - Test system activation and deactivation
    - _Requirements: 1.5, 3.1, 3.4, 9.2, 9.3_

- [ ] 12. Create configuration management
  - [ ] 12.1 Implement Config class
    - Define all configuration parameters
    - Load from config file or use defaults
    - Provide validation for configuration values
    - _Requirements: 1.1, 2.2, 2.3, 4.4, 5.2_
  
  - [ ]* 12.2 Write unit tests for configuration
    - Test default values (48kHz, 0.03 threshold, 0.50 confidence, etc.)
    - Test configuration validation
    - Test configuration loading
    - _Requirements: 1.1, 2.2, 2.3_

- [ ] 13. Final checkpoint - Run full test suite
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 14. Create entry point and packaging
  - [ ] 14.1 Create main entry point script
    - Initialize all components
    - Handle PyInstaller splash screen
    - Start Tkinter main loop
    - _Requirements: All_
  
  - [ ] 14.2 Add documentation
    - Create README with setup instructions
    - Document configuration options
    - Document system requirements
    - Add usage examples

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation at key milestones
- Property tests validate universal correctness properties (100+ iterations each)
- Unit tests validate specific examples, edge cases, and error conditions
- The refactoring preserves all existing functionality while improving testability and maintainability
- All components should be independently testable with mocked dependencies
