from assistant.commands import interpret

def test_interpret():
    assert interpret("öffne youtube") == "OPEN_YOUTUBE"
    assert interpret("Stopp") == "STOP"
    assert interpret("Was ist das Wetter?") == "UNKNOWN"