from datetime import date, timedelta


def sm2(quality: int, ef: float, interval: int, repetitions: int) -> tuple[float, int, int, date]:
    if quality >= 3:
        if repetitions == 0:
            interval = 1
        elif repetitions == 1:
            interval = 6
        else:
            interval = round(interval * ef)
        repetitions += 1
    else:
        repetitions = 0
        interval = 1

    ef = ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    ef = max(1.3, ef)

    next_review = date.today() + timedelta(days=interval)

    return ef, interval, repetitions, next_review
