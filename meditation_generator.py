# meditation_generator.py

import numpy as np
from scipy import signal
import soundfile as sf
from datetime import datetime
import os
from gtts import gTTS
from pydub import AudioSegment
import tempfile
import pyroomacoustics as pra
from scipy.spatial.transform import Rotation
import librosa
import python_speech_features

class SpatialAudioProcessor:
    """
    Handles spatial audio processing and 3D sound positioning.
    """
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.room_dim = [5, 5, 3]  # Room dimensions in meters
        self.rt60 = 0.3  # Reverberation time
        self.room = pra.ShoeBox(
            self.room_dim,
            fs=sample_rate,
            materials=pra.Material(0.2),
            max_order=3
        )

    def create_spatial_effect(self, audio, position=(0, 0, 0), movement=None):
        """
        Apply spatial positioning and movement to audio.
        
        Args:
            audio: Input audio array
            position: (x, y, z) coordinates in the virtual room
            movement: Dictionary with movement pattern and speed
        """
        # Convert mono to stereo if necessary
        if len(audio.shape) == 1:
            audio = np.stack([audio, audio]).T
        
        # Reset room before adding new source
        self.room = pra.ShoeBox(
            self.room_dim,
            fs=self.sample_rate,
            materials=pra.Material(0.2),
            max_order=3
        )
        
        # Add audio source and microphone array
        self.room.add_source(position, signal=audio[:, 0])
        R = pra.circular_2D_array(center=[2.5, 2.5], M=2, phi0=0, radius=0.0875)
        self.room.add_microphone_array(R)
        
        # Compute room acoustics
        self.room.compute_rir()
        output = self.room.simulate()
        
        # Apply movement if specified
        if movement:
            output = self._apply_movement(output, movement)
        
        return output.T

    def _apply_movement(self, audio, movement):
        """
        Apply movement effects to the audio.
        
        Args:
            audio: Input audio array
            movement: Dictionary containing pattern and speed
        """
        pattern = movement.get('pattern', 'circular')
        speed = movement.get('speed', 0.5)
        
        samples = len(audio)
        t = np.linspace(0, samples/self.sample_rate, samples)
        
        if pattern == 'circular':
            angle = 2 * np.pi * speed * t
            x = np.cos(angle)
            y = np.sin(angle)
            z = np.zeros_like(t)
        elif pattern == 'spiral':
            angle = 2 * np.pi * speed * t
            x = t * np.cos(angle)
            y = t * np.sin(angle)
            z = t
        
        # Apply movement using rotation matrices
        output = np.zeros_like(audio)
        for i in range(len(t)):
            rotation = Rotation.from_euler('xyz', [x[i], y[i], z[i]])
            output[i] = rotation.apply(audio[i])
            
        return output

class AdvancedAudioGenerator:
    """
    Main class for generating meditation audio with various effects.
    """
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        self.spatial_processor = SpatialAudioProcessor(sample_rate)
        
        # Define brainwave frequency ranges
        self.brainwave_states = {
            'gamma': (30, 50),    # Enhanced perception
            'beta': (14, 30),     # Active thinking
            'alpha': (8, 14),     # Relaxed awareness
            'theta': (4, 8),      # Deep meditation
            'delta': (0.5, 4),    # Deep sleep
        }
        
        # Define special sound parameters
        self.special_sounds = {
            'crystal_bowls': {
                'frequencies': [396, 417, 528, 639, 741, 852],  # Solfeggio frequencies
                'duration': 3.0,
                'position': (2.5, 2.5, 1.5)
            },
            'om_chant': {
                'base_freq': 136.1,  # Om frequency
                'harmonics': [2, 3, 4],
                'duration': 4.0,
                'position': (2.5, 0, 1.5)
            },
            'wind_chimes': {
                'frequencies': [1318.51, 1174.66, 880, 987.77, 783.99],  # Pentatonic scale
                'duration': 2.0,
                'position': (0, 2.5, 2)
            }
        }

    def generate_special_sound(self, sound_type, duration=None):
        """
        Generate special meditation sounds with spatial positioning.
        """
        if sound_type not in self.special_sounds:
            raise ValueError(f"Unknown sound type: {sound_type}")
            
        sound_params = self.special_sounds[sound_type]
        duration = duration or sound_params['duration']
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        if sound_type == 'crystal_bowls':
            audio = np.zeros_like(t)
            for freq in sound_params['frequencies']:
                # Generate pure sine waves with harmonics
                audio += np.sin(2 * np.pi * freq * t) * 0.5
                audio += np.sin(2 * np.pi * freq * 2 * t) * 0.25
                audio += np.sin(2 * np.pi * freq * 3 * t) * 0.125
                
        elif sound_type == 'om_chant':
            audio = np.sin(2 * np.pi * sound_params['base_freq'] * t)
            for harmonic in sound_params['harmonics']:
                audio += np.sin(2 * np.pi * sound_params['base_freq'] * harmonic * t) * (1/harmonic)
                
        elif sound_type == 'wind_chimes':
            audio = np.zeros_like(t)
            for freq in sound_params['frequencies']:
                # Random timing for each chime
                start_times = np.random.rand(5) * duration
                for start in start_times:
                    idx = int(start * self.sample_rate)
                    if idx + 44100 < len(audio):  # 1-second chime
                        chime = np.sin(2 * np.pi * freq * t[:44100]) * np.exp(-t[:44100] * 5)
                        audio[idx:idx + 44100] += chime
        
        # Normalize audio
        audio = audio / np.max(np.abs(audio))
        
        # Apply spatial processing
        return self.spatial_processor.create_spatial_effect(
            audio,
            position=sound_params['position'],
            movement={'pattern': 'circular', 'speed': 0.2}
        )

    def create_atmos_mix(self, sounds, duration):
        """
        Create a mix of special sounds with spatial positioning.
        """
        output = np.zeros((int(self.sample_rate * duration), 2))
        
        for sound_type in sounds:
            sound = self.generate_special_sound(sound_type, duration)
            if len(sound) < len(output):
                sound = np.pad(sound, ((0, len(output) - len(sound)), (0, 0)))
            else:
                sound = sound[:len(output)]
            output += sound * (1.0 / len(sounds))
            
        return output

    def generate_voice_guidance(self, script):
        """
        Generate voice guidance audio using text-to-speech.
        """
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            # Generate speech
            tts = gTTS(text=script, lang='en', slow=False)
            tts.save(temp_file.name)
            
            # Load and convert to numpy array
            audio = AudioSegment.from_mp3(temp_file.name)
            samples = np.array(audio.get_array_of_samples())
            
        # Convert to float32 and normalize
        samples = samples.astype(np.float32) / np.iinfo(np.int16).max
        
        # Convert mono to stereo if necessary
        if len(samples.shape) == 1:
            samples = np.column_stack((samples, samples))
            
        return samples

    def save_session(self, audio, filename):
        """
        Save the generated meditation session to a file.
        """
        # Create output directory if it doesn't exist
        os.makedirs('output', exist_ok=True)
        
        # Add timestamp to filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"output/{timestamp}_{filename}"
        
        # Save the audio file
        sf.write(filename, audio, self.sample_rate)
        return filename

    def create_guided_meditation(self, duration, target_state='alpha', special_sounds=None, custom_script=None):
        """
        Create a complete guided meditation session.
        
        Args:
            duration: Length of meditation in seconds
            target_state: Desired brainwave state
            special_sounds: List of special sound types to include
            custom_script: Text for voice guidance
        """
        # Generate special sounds mix or simple binaural beats
        if special_sounds:
            base_audio = self.create_atmos_mix(special_sounds, duration)
        else:
            t = np.linspace(0, duration, int(self.sample_rate * duration))
            freq = np.mean(self.brainwave_states[target_state])
            base_audio = np.sin(2 * np.pi * freq * t)
            base_audio = np.column_stack((base_audio, base_audio))

        # Add voice guidance if script provided
        if custom_script:
            voice_audio = self.generate_voice_guidance(custom_script)
            voice_audio = self.spatial_processor.create_spatial_effect(
                voice_audio,
                position=(2.5, 2.5, 1.7)  # Position voice slightly above listener
            )
            
            # Match lengths and mix
            if len(voice_audio) < len(base_audio):
                voice_audio = np.pad(voice_audio, ((0, len(base_audio) - len(voice_audio)), (0, 0)))
            else:
                voice_audio = voice_audio[:len(base_audio)]
            
            mixed_audio = voice_audio + (base_audio * 0.3)
        else:
            mixed_audio = base_audio
        
        # Final normalization
        mixed_audio = mixed_audio / np.max(np.abs(mixed_audio))
        
        return mixed_audio
