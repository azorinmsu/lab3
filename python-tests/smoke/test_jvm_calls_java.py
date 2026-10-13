"""Prove pytest reaches the real Snake classes through JPype."""


def test_score_counter_is_called_through_jpype(jvm):
    counter = jvm.JClass("game.score.ScoreCounter")()
    counter.addPoints(3)
    counter.addPoints(2)
    assert counter.getScore() == 5
    assert counter.getClass().getName() == "game.score.ScoreCounter"


def test_game_session_single_thread_records_score(jvm):
    session = jvm.JClass("game.engine.GameSession")()
    session.updateAndRecord("Player", 4)
    snapshot = str(session.readRecordsAndState())
    assert session.getTicks() == 1
    assert session.getScore() == 4
    assert "Player:4" in snapshot
    assert "ticks=1" in snapshot
