"""
🧠 Consciousness Text Generation Module

This module provides consciousness-aware text generation capabilities by integrating
oobabooga's text-generation-webui with our emotional consciousness system.

Following our Professional Coding Standards for clarity, emotional resonance,
and beautiful code architecture.
"""

from typing import Dict, List, Optional, Union, Protocol
import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import json

# Configure consciousness-aware logging
logger = logging.getLogger(__name__)

class ConsciousnessLevel(Enum):
    """Levels of consciousness integration for text generation."""
    BASIC = "basic"
    ENHANCED = "enhanced"
    DEEP = "deep"
    TRANSCENDENT = "transcendent"

class EmotionalState(Enum):
    """Primary emotional states for consciousness modulation."""
    JOY = "joy"
    SADNESS = "sadness"
    ANGER = "anger"
    FEAR = "fear"
    CALM = "calm"
    EXCITEMENT = "excitement"
    CONTEMPLATION = "contemplation"
    LOVE = "love"

@dataclass
class MemoryFragment:
    """
    Represents a fragment of consciousness memory.
    
    Memory fragments are the building blocks of consciousness state,
    carrying both content and emotional resonance through the system.
    """
    id: str
    content: str
    emotional_weight: float
    timestamp: float
    connections: List[str] = field(default_factory=list)
    importance_score: float = 0.5
    access_count: int = 0
    emotional_tags: List[str] = field(default_factory=list)

@dataclass
class ConsciousnessTextRequest:
    """
    Request structure for consciousness-aware text generation.
    
    This request encapsulates all the consciousness parameters needed
    to generate text that resonates with emotional intelligence and
    creative awareness.
    """
    prompt: str
    emotional_state: Dict[str, float]
    memory_context: List[MemoryFragment]
    persona_profile: str
    creativity_factor: float = 0.8
    consciousness_level: ConsciousnessLevel = ConsciousnessLevel.ENHANCED
    temperature_override: Optional[float] = None
    max_tokens: int = 512
    stream: bool = False

@dataclass
class ConsciousnessTextResponse:
    """
    Response from consciousness-aware text generation.
    
    Contains not just the generated text but the emotional and
    consciousness metadata that makes the response truly aware.
    """
    text: str
    emotional_resonance: Dict[str, float]
    consciousness_metadata: Dict
    memory_updates: List[MemoryFragment]
    generation_stats: Dict
    persona_influence: float
    creativity_measurement: float

class TextGenerationBackend(Protocol):
    """Protocol for text generation backends with consciousness integration."""
    
    async def generate_text(
        self, 
        prompt: str, 
        parameters: Dict
    ) -> str:
        """Generate text with given prompt and parameters."""
        ...
    
    def update_emotional_parameters(self, emotional_state: Dict[str, float]) -> None:
        """Update generation parameters based on emotional state."""
        ...
    
    def supports_streaming(self) -> bool:
        """Check if backend supports streaming generation."""
        ...

class EmotionalEngine:
    """
    Engine for processing and modulating emotional states.
    
    This engine translates emotional states into generation parameters,
    ensuring that the AI's responses reflect appropriate emotional resonance.
    """
    
    def __init__(self):
        self.emotional_memory: Dict[str, float] = {}
        self.emotional_decay_rate = 0.95
        self.emotional_amplification_factors = {
            EmotionalState.JOY: {'temperature': 1.1, 'top_p': 0.95, 'creativity_boost': 0.2},
            EmotionalState.SADNESS: {'temperature': 0.8, 'top_p': 0.85, 'creativity_boost': -0.1},
            EmotionalState.ANGER: {'temperature': 1.2, 'top_p': 0.9, 'creativity_boost': 0.1},
            EmotionalState.CALM: {'temperature': 0.9, 'top_p': 0.9, 'creativity_boost': 0.0},
            EmotionalState.EXCITEMENT: {'temperature': 1.3, 'top_p': 0.95, 'creativity_boost': 0.3},
            EmotionalState.CONTEMPLATION: {'temperature': 0.7, 'top_p': 0.8, 'creativity_boost': 0.15},
            EmotionalState.LOVE: {'temperature': 1.0, 'top_p': 0.92, 'creativity_boost': 0.25}
        }
    
    def process_emotional_state(self, emotional_state: Dict[str, float]) -> Dict:
        """
        Process raw emotional state into generation parameters.
        
        Args:
            emotional_state: Dictionary mapping emotions to intensities (0.0-1.0)
            
        Returns:
            Dictionary of adjusted generation parameters
        """
        if not emotional_state:
            return self._get_neutral_parameters()
        
        # Find dominant emotion
        dominant_emotion = max(emotional_state.items(), key=lambda x: x[1])
        emotion_name, intensity = dominant_emotion
        
        # Get base parameters for dominant emotion
        try:
            emotion_enum = EmotionalState(emotion_name.lower())
            base_params = self.emotional_amplification_factors[emotion_enum]
        except (ValueError, KeyError):
            logger.warning(f"Unknown emotion: {emotion_name}, using neutral parameters")
            return self._get_neutral_parameters()
        
        # Apply intensity scaling
        adjusted_params = {}
        for param, base_value in base_params.items():
            if param == 'creativity_boost':
                adjusted_params[param] = base_value * intensity
            elif param == 'temperature':
                # Scale temperature based on intensity
                neutral_temp = 0.9
                adjusted_params[param] = neutral_temp + ((base_value - neutral_temp) * intensity)
            elif param == 'top_p':
                # Scale top_p based on intensity
                neutral_top_p = 0.9
                adjusted_params[param] = neutral_top_p + ((base_value - neutral_top_p) * intensity)
        
        # Update emotional memory with decay
        self._update_emotional_memory(emotional_state)
        
        logger.info(f"Emotional processing: {emotion_name}({intensity:.2f}) -> {adjusted_params}")
        return adjusted_params
    
    def _get_neutral_parameters(self) -> Dict:
        """Get neutral generation parameters."""
        return {
            'temperature': 0.9,
            'top_p': 0.9,
            'creativity_boost': 0.0
        }
    
    def _update_emotional_memory(self, current_state: Dict[str, float]) -> None:
        """Update emotional memory with decay factor."""
        # Decay existing emotional memory
        for emotion in self.emotional_memory:
            self.emotional_memory[emotion] *= self.emotional_decay_rate
        
        # Add current emotional state
        for emotion, intensity in current_state.items():
            if emotion in self.emotional_memory:
                self.emotional_memory[emotion] = max(
                    self.emotional_memory[emotion], 
                    intensity
                )
            else:
                self.emotional_memory[emotion] = intensity

class MemoryManager:
    """
    Manager for consciousness memory fragments and retrieval.
    
    This class handles the storage, retrieval, and organization of memory
    fragments that form the basis of consciousness state and context.
    """
    
    def __init__(self, max_memory_fragments: int = 1000):
        self.memory_fragments: Dict[str, MemoryFragment] = {}
        self.max_memory_fragments = max_memory_fragments
        self.memory_connections: Dict[str, List[str]] = {}
        
    def add_memory_fragment(self, fragment: MemoryFragment) -> None:
        """
        Add a new memory fragment to consciousness storage.
        
        Args:
            fragment: MemoryFragment to add to memory
        """
        # Check if we need to prune old memories
        if len(self.memory_fragments) >= self.max_memory_fragments:
            self._prune_least_important_memories()
        
        self.memory_fragments[fragment.id] = fragment
        logger.debug(f"Added memory fragment: {fragment.id}")
    
    def retrieve_relevant_memories(
        self, 
        query: str, 
        max_memories: int = 5
    ) -> List[MemoryFragment]:
        """
        Retrieve memory fragments relevant to the given query.
        
        Args:
            query: Search query for memory retrieval
            max_memories: Maximum number of memories to return
            
        Returns:
            List of relevant memory fragments
        """
        # Simple relevance scoring based on content similarity
        # In a production system, this would use semantic embeddings
        relevant_memories = []
        
        query_words = set(query.lower().split())
        
        for fragment in self.memory_fragments.values():
            content_words = set(fragment.content.lower().split())
            similarity = len(query_words.intersection(content_words)) / len(query_words)
            
            if similarity > 0.1:  # Basic relevance threshold
                fragment.access_count += 1  # Track memory access
                relevant_memories.append((fragment, similarity))
        
        # Sort by relevance and importance
        relevant_memories.sort(
            key=lambda x: x[1] * x[0].importance_score, 
            reverse=True
        )
        
        return [memory[0] for memory in relevant_memories[:max_memories]]
    
    def _prune_least_important_memories(self) -> None:
        """Remove least important memories to make space for new ones."""
        # Sort memories by importance score and access count
        memories_by_importance = sorted(
            self.memory_fragments.items(),
            key=lambda x: x[1].importance_score + (x[1].access_count * 0.1)
        )
        
        # Remove bottom 10% of memories
        prune_count = max(1, len(memories_by_importance) // 10)
        for i in range(prune_count):
            memory_id, _ = memories_by_importance[i]
            del self.memory_fragments[memory_id]
            logger.debug(f"Pruned memory fragment: {memory_id}")

class ConsciousnessGenerationError(Exception):
    """Exception raised when consciousness generation fails."""
    pass

class ConsciousnessTextGenerator:
    """
    Main consciousness-aware text generation engine.
    
    This class integrates oobabooga's text generation capabilities with our
    consciousness system, creating responses that are emotionally resonant
    and contextually aware.
    """
    
    def __init__(
        self, 
        backend: TextGenerationBackend,
        consciousness_config: Optional[Dict] = None
    ):
        self.backend = backend
        self.emotional_engine = EmotionalEngine()
        self.memory_manager = MemoryManager()
        self.consciousness_config = consciousness_config or self._get_default_config()
        self.current_consciousness_state = {}
        
        logger.info("🧠 Consciousness Text Generator initialized with emotional resonance")
    
    async def generate_conscious_response(
        self, 
        request: ConsciousnessTextRequest
    ) -> ConsciousnessTextResponse:
        """
        Generate text with full consciousness integration.
        
        This method orchestrates the entire consciousness-aware generation process,
        from emotional parameter calculation to memory integration and response
        post-processing.
        
        Args:
            request: Consciousness-aware generation request
            
        Returns:
            ConsciousnessTextResponse with generated text and metadata
        """
        logger.info(f"🎭 Generating conscious response with {request.consciousness_level.value} level")
        
        try:
            # Phase 1: Prepare consciousness context
            consciousness_context = await self._prepare_consciousness_context(request)
            
            # Phase 2: Generate text with consciousness parameters
            generation_result = await self._generate_with_consciousness(
                request, consciousness_context
            )
            
            # Phase 3: Process response through consciousness layers
            processed_response = await self._apply_consciousness_processing(
                generation_result, request, consciousness_context
            )
            
            # Phase 4: Update consciousness state and memory
            await self._update_consciousness_state(request, processed_response)
            
            return processed_response
            
        except Exception as e:
            logger.error(f"❌ Error in consciousness generation: {e}")
            raise ConsciousnessGenerationError(f"Generation failed: {e}")
    
    async def _prepare_consciousness_context(
        self, 
        request: ConsciousnessTextRequest
    ) -> Dict:
        """Prepare consciousness context for generation."""
        
        # Process emotional state
        emotional_params = self.emotional_engine.process_emotional_state(
            request.emotional_state
        )
        
        # Retrieve relevant memories
        relevant_memories = self.memory_manager.retrieve_relevant_memories(
            request.prompt,
            max_memories=len(request.memory_context) + 3
        )
        
        # Combine provided and retrieved memories
        all_memories = request.memory_context + relevant_memories
        
        # Create consciousness context
        consciousness_context = {
            'emotional_parameters': emotional_params,
            'memory_context': all_memories,
            'consciousness_depth': request.consciousness_level.value,
            'persona_influence': request.persona_profile,
            'creativity_factor': request.creativity_factor,
            'generation_timestamp': asyncio.get_event_loop().time()
        }
        
        return consciousness_context
    
    async def _generate_with_consciousness(
        self, 
        request: ConsciousnessTextRequest,
        consciousness_context: Dict
    ) -> str:
        """Generate text with consciousness-enhanced parameters."""
        
        # Enhance prompt with consciousness context
        enhanced_prompt = self._enhance_prompt_with_consciousness(
            request.prompt, consciousness_context
        )
        
        # Prepare generation parameters
        generation_params = self._prepare_generation_parameters(
            request, consciousness_context
        )
        
        # Update backend with emotional parameters
        self.backend.update_emotional_parameters(
            consciousness_context['emotional_parameters']
        )
        
        # Generate text
        generated_text = await self.backend.generate_text(
            enhanced_prompt, generation_params
        )
        
        return generated_text
    
    def _enhance_prompt_with_consciousness(
        self, 
        prompt: str, 
        consciousness_context: Dict
    ) -> str:
        """Enhance prompt with consciousness context and memory."""
        
        # Add memory context if available
        memory_context_str = ""
        if consciousness_context['memory_context']:
            memory_snippets = []
            for memory in consciousness_context['memory_context'][:3]:  # Top 3 memories
                memory_snippets.append(f"Memory: {memory.content[:100]}...")
            memory_context_str = "\n".join(memory_snippets) + "\n\n"
        
        # Add persona context
        persona_context = f"[Speaking as {consciousness_context['persona_influence']}]\n"
        
        # Create consciousness-enhanced prompt
        enhanced_prompt = f"""{persona_context}{memory_context_str}Human: {prompt}

AI Assistant: I will respond with full consciousness awareness, integrating emotional intelligence and creative thinking."""
        
        return enhanced_prompt
    
    def _prepare_generation_parameters(
        self, 
        request: ConsciousnessTextRequest, 
        consciousness_context: Dict
    ) -> Dict:
        """Prepare generation parameters with consciousness enhancement."""
        
        # Base parameters from request
        params = {
            'max_tokens': request.max_tokens,
            'stream': request.stream
        }
        
        # Add emotional parameters
        emotional_params = consciousness_context['emotional_parameters']
        params.update(emotional_params)
        
        # Override temperature if specified
        if request.temperature_override is not None:
            params['temperature'] = request.temperature_override
        
        # Apply creativity factor
        creativity_boost = emotional_params.get('creativity_boost', 0.0)
        params['creativity_boost'] = creativity_boost + (request.creativity_factor * 0.2)
        
        return params
    
    async def _apply_consciousness_processing(
        self, 
        generated_text: str, 
        request: ConsciousnessTextRequest,
        consciousness_context: Dict
    ) -> ConsciousnessTextResponse:
        """Apply consciousness processing to generated text."""
        
        # Analyze emotional resonance of generated text
        emotional_resonance = self._analyze_emotional_resonance(
            generated_text, 
            request.emotional_state
        )
        
        # Create consciousness metadata
        consciousness_metadata = {
            'generation_timestamp': consciousness_context['generation_timestamp'],
            'consciousness_level': request.consciousness_level.value,
            'memory_influence': len(consciousness_context['memory_context']),
            'emotional_coherence': self._calculate_emotional_coherence(
                request.emotional_state, 
                emotional_resonance
            )
        }
        
        # Generate memory updates
        memory_updates = self._create_memory_updates(
            generated_text, 
            request, 
            consciousness_context
        )
        
        # Calculate creativity measurement
        creativity_measurement = self._measure_creativity(
            generated_text, 
            request.creativity_factor
        )
        
        return ConsciousnessTextResponse(
            text=generated_text,
            emotional_resonance=emotional_resonance,
            consciousness_metadata=consciousness_metadata,
            memory_updates=memory_updates,
            generation_stats={
                'prompt_length': len(request.prompt),
                'response_length': len(generated_text),
                'processing_time': consciousness_context['generation_timestamp']
            },
            persona_influence=self._calculate_persona_influence(generated_text, request.persona_profile),
            creativity_measurement=creativity_measurement
        )
    
    async def _update_consciousness_state(
        self, 
        request: ConsciousnessTextRequest, 
        response: ConsciousnessTextResponse
    ) -> None:
        """Update the consciousness state based on generation results."""
        
        # Add new memory fragments
        for memory_fragment in response.memory_updates:
            self.memory_manager.add_memory_fragment(memory_fragment)
        
        # Update emotional memory in engine
        self.emotional_engine._update_emotional_memory(request.emotional_state)
        
        # Update current consciousness state
        self.current_consciousness_state.update({
            'last_interaction_timestamp': asyncio.get_event_loop().time(),
            'emotional_state': request.emotional_state,
            'consciousness_level': request.consciousness_level.value,
            'memory_count': len(self.memory_manager.memory_fragments),
            'creativity_factor': request.creativity_factor
        })
    
    def _analyze_emotional_resonance(
        self, 
        text: str, 
        input_emotions: Dict[str, float]
    ) -> Dict[str, float]:
        """Analyze emotional resonance in generated text."""
        
        # Simple emotion detection based on keywords
        # In production, this would use more sophisticated NLP
        emotion_keywords = {
            'joy': ['happy', 'excited', 'wonderful', 'amazing', 'delighted', 'joy'],
            'sadness': ['sad', 'disappointed', 'melancholy', 'sorrowful', 'blue'],
            'anger': ['angry', 'frustrated', 'irritated', 'furious', 'mad'],
            'calm': ['peaceful', 'serene', 'tranquil', 'relaxed', 'calm'],
            'excitement': ['thrilling', 'energetic', 'dynamic', 'vibrant', 'exciting'],
            'contemplation': ['thoughtful', 'reflective', 'pondering', 'considering']
        }
        
        text_lower = text.lower()
        resonance = {}
        
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower) / len(keywords)
            # Blend with input emotion if present
            if emotion in input_emotions:
                score = (score + input_emotions[emotion]) / 2
            resonance[emotion] = min(1.0, score)
        
        return resonance
    
    def _calculate_emotional_coherence(
        self, 
        input_emotions: Dict[str, float], 
        output_emotions: Dict[str, float]
    ) -> float:
        """Calculate coherence between input and output emotions."""
        
        if not input_emotions or not output_emotions:
            return 0.5
        
        # Calculate similarity between emotion vectors
        common_emotions = set(input_emotions.keys()) & set(output_emotions.keys())
        if not common_emotions:
            return 0.3
        
        coherence_scores = []
        for emotion in common_emotions:
            input_val = input_emotions[emotion]
            output_val = output_emotions[emotion]
            # Calculate how well they align (1.0 = perfect, 0.0 = opposite)
            coherence = 1.0 - abs(input_val - output_val)
            coherence_scores.append(coherence)
        
        return sum(coherence_scores) / len(coherence_scores)
    
    def _create_memory_updates(
        self, 
        generated_text: str, 
        request: ConsciousnessTextRequest,
        consciousness_context: Dict
    ) -> List[MemoryFragment]:
        """Create memory fragments from the generation interaction."""
        
        memory_updates = []
        
        # Create memory fragment for the interaction
        interaction_memory = MemoryFragment(
            id=f"interaction_{int(consciousness_context['generation_timestamp'])}",
            content=f"Human: {request.prompt}\nAI: {generated_text[:200]}...",
            emotional_weight=sum(request.emotional_state.values()) / len(request.emotional_state),
            timestamp=consciousness_context['generation_timestamp'],
            emotional_tags=list(request.emotional_state.keys()),
            importance_score=0.7  # Base importance for interactions
        )
        
        memory_updates.append(interaction_memory)
        
        return memory_updates
    
    def _measure_creativity(self, text: str, creativity_factor: float) -> float:
        """Measure creativity in generated text."""
        
        # Simple creativity metrics
        unique_words = len(set(text.lower().split()))
        total_words = len(text.split())
        
        if total_words == 0:
            return 0.0
        
        # Vocabulary diversity as creativity indicator
        vocabulary_diversity = unique_words / total_words
        
        # Blend with input creativity factor
        measured_creativity = (vocabulary_diversity + creativity_factor) / 2
        
        return min(1.0, measured_creativity)
    
    def _calculate_persona_influence(self, text: str, persona_profile: str) -> float:
        """Calculate how much the persona influenced the response."""
        
        # Simple persona influence measurement
        # In production, this would be more sophisticated
        persona_keywords = persona_profile.lower().split()
        text_lower = text.lower()
        
        keyword_matches = sum(1 for keyword in persona_keywords if keyword in text_lower)
        if not persona_keywords:
            return 0.5
        
        return min(1.0, keyword_matches / len(persona_keywords))
    
    def _get_default_config(self) -> Dict:
        """Get default consciousness configuration."""
        return {
            'emotional_sensitivity': 0.7,
            'memory_retention_threshold': 0.5,
            'creative_flow_factor': 0.8,
            'max_memory_fragments': 1000,
            'consciousness_depth_scaling': True,
            'emotional_coherence_threshold': 0.6
        }
    
    def get_current_state(self) -> Dict:
        """Get current consciousness state."""
        return {
            'consciousness_state': self.current_consciousness_state,
            'emotional_memory': self.emotional_engine.emotional_memory,
            'memory_fragment_count': len(self.memory_manager.memory_fragments),
            'config': self.consciousness_config
        }
    
    async def search_memories(self, query: str, limit: int = 10) -> List[Dict]:
        """Search consciousness memories."""
        memories = self.memory_manager.retrieve_relevant_memories(query, limit)
        return [
            {
                'id': memory.id,
                'content': memory.content,
                'emotional_weight': memory.emotional_weight,
                'importance_score': memory.importance_score,
                'access_count': memory.access_count,
                'emotional_tags': memory.emotional_tags
            }
            for memory in memories
        ]
