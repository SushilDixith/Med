# generate_session.py

from meditation_generator import AdvancedAudioGenerator

def create_meditation_session():
    generator = AdvancedAudioGenerator()
    
    # 10 minutes = 600 seconds
    duration = 600
    
    # Extended script with appropriate pacing for 10 minutes
    custom_script = """
    Welcome to this ten-minute meditation journey.
    Find a comfortable position, and gently close your eyes.
    [Pause]
    Take a deep breath in... and slowly exhale...
    Allow each breath to help you settle more deeply into relaxation.
    [Pause]
    Feel the peaceful sounds surrounding you in space.
    The crystal bowls and sacred chants will guide you into a deeper state of consciousness.
    [Long Pause]
    Notice any tension in your body... and with each exhale, let it dissolve away.
    [Pause]
    The sounds are creating a cocoon of peaceful energy around you.
    Simply observe their gentle movement...
    [Long Pause]
    If thoughts arise, let them pass by like clouds in the sky.
    There's nothing you need to do... nowhere you need to go...
    [Very Long Pause]
    Allow the healing vibrations to wash over you...
    Bringing peace to every cell of your being...
    [Long Pause]
    In these next few moments, simply rest in awareness...
    [Very Long Pause]
    As we begin to conclude this meditation...
    Gradually become aware of your breath once again...
    [Pause]
    Feel the points where your body makes contact with the surface beneath you...
    [Pause]
    When you're ready, slowly wiggle your fingers and toes...
    Take a deep breath in...
    And gently open your eyes...
    Carrying this sense of peace with you into the rest of your day.
    """
    
    # Generate the meditation audio
    audio = generator.create_guided_meditation(
        duration=duration,
        target_state='theta',  # Theta state is ideal for deep meditation
        special_sounds=['crystal_bowls', 'om_chant', 'wind_chimes'],  # Using all available sounds
        custom_script=custom_script
    )
    
    # Save the generated audio
    filename = generator.save_session(audio, "meditation_10min.wav")
    print(f"10-minute meditation session saved to: {filename}")

if __name__ == "__main__":
    create_meditation_session()
