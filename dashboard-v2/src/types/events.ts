/**
 * Base interface for all Coda events
 */
export interface CodaEvent {
  type: string;
  timestamp: number;
  [key: string]: any;
}

/**
 * Event for when the STT module starts listening
 */
export interface ListeningStartEvent extends CodaEvent {
  type: 'listening_start';
}

/**
 * Event for when the STT module stops listening
 */
export interface ListeningStopEvent extends CodaEvent {
  type: 'listening_stop';
}

/**
 * Event for when the STT module recognizes speech
 */
export interface SpeechRecognizedEvent extends CodaEvent {
  type: 'speech_recognized';
  text: string;
  confidence: number;
}

/**
 * Event for when the LLM starts processing
 */
export interface LLMProcessingStartEvent extends CodaEvent {
  type: 'llm_processing_start';
  input: string;
}

/**
 * Event for when the LLM finishes processing
 */
export interface LLMProcessingCompleteEvent extends CodaEvent {
  type: 'llm_processing_complete';
  output: string;
  processingTime: number;
}

/**
 * Event for when the TTS starts speaking
 */
export interface SpeakingStartEvent extends CodaEvent {
  type: 'speaking_start';
  text: string;
}

/**
 * Event for when the TTS stops speaking
 */
export interface SpeakingStopEvent extends CodaEvent {
  type: 'speaking_stop';
  duration: number;
}

/**
 * Event for when a tool is used
 */
export interface ToolUsedEvent extends CodaEvent {
  type: 'tool_used';
  toolName: string;
  input: any;
  output: any;
  duration: number;
}

/**
 * Event for when a memory is created or accessed
 */
export interface MemoryEvent extends CodaEvent {
  type: 'memory_created' | 'memory_accessed';
  memoryId: string;
  content: string;
}

/**
 * Event for when an error occurs
 */
export interface ErrorEvent extends CodaEvent {
  type: 'error';
  error: string;
  component: string;
}

/**
 * Union type of all Coda events
 */
export type CodaEventTypes =
  | ListeningStartEvent
  | ListeningStopEvent
  | SpeechRecognizedEvent
  | LLMProcessingStartEvent
  | LLMProcessingCompleteEvent
  | SpeakingStartEvent
  | SpeakingStopEvent
  | ToolUsedEvent
  | MemoryEvent
  | ErrorEvent;
