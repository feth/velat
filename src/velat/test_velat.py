from .velat import Velat

def _mkvelat():
    return Velat()

def test_newinstance():
    return _mkvelat()

def test_newperson():
    velat = _mkvelat()
    person = velat.newperson("person")

def test_functionnal():
    velat = _mkvelat()
    pers1 = velat.newperson("pers1")
    cinema = velat.newexpense("cinema")
    cinema.newtakepart(pers1, shares=1)
    #nobody paid the cinema, therefore it is free
    assert velat.solve() == [(pers1, None, 0.0)]
    pers2 = velat.newperson("pers2")
    cinema.newtakepart(pers2, shares=1)
    #still free
    assert set(velat.solve()) == set([(pers1, None, 0.0), (pers2, None, 0.0)])
    pers3 = velat.newperson("pers3")
    #uh oh, someone paid 42
    cinema.newtakepart(pers3, paid=42)
    #therefore the 2 other owe him 42/2
    assert set(velat.solve()) == set([
        (pers1, pers3, 21.0),
        (pers2, pers3, 21.0),
        ])
    #soemone took a seat and paid 10
    pers4 = velat.newperson("pers4")
    cinema.newtakepart(pers4, shares=1, paid=12)
    assert set(velat.solve()) == set([
        (pers1, pers3, 18.0),
        (pers2, pers3, 18.0),
        (pers4, pers3, 6.0),
        ])

    #5 only chew popcorns: cost=6
    pers5 = velat.newperson("pers5")
    cinema.newtakepart(pers5, taken=6)
    assert set(velat.solve()) == set([
        (pers1, pers3, 16.0),
        (pers2, pers3, 16.0),
        (pers4, pers3, 4.0),
        (pers5, pers3, 6.0),
        ])

    #actually, all of this was much more expensive
    #6 took a seat and popcorns, and paid for the rest
    pers6 = velat.newperson("pers6")
    cinema.newtakepart(pers6, shares=1, paid=48, taken=6)
    #several solutions
    assert set(velat.solve()) in (
        set([
            (pers2, pers3, 22.5),
            (pers1, pers3, 19.5),
            (pers1, pers6, 3),
            (pers4, pers6, 10.5),
            (pers5, pers6, 6.0),
        ]),
        set([
            (pers1, pers3, 22.5),
            (pers2, pers3, 19.5),
            (pers2, pers6, 3),
            (pers4, pers6, 10.5),
            (pers5, pers6, 6.0),
        ]),
        #and some other?
    )
    #pers7 went to restaurant with pers6, and paid
    restaurant = velat.newexpense("restaurant")
    pers7 = velat.newperson("pers7")
    restaurant.newtakepart(pers7, shares=1, paid=100)
    restaurant.newtakepart(pers6, shares=1)
    assert set(velat.solve()) in (
        set(
            [(pers6, pers7, 30.5),
             (pers2, pers3, 22.5),
             (pers1, pers3, 19.5),
             (pers4, pers7, 10.5),
             (pers5, pers7, 6.0),
             (pers1, pers7, 3.0)]
        ),
        #and some other?
    )

