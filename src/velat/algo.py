def _exactmmatch(personstotals, total):
    """
    personstotals is expected as a list of (person, credit)
    The sign of credit is opposite to the sign of total and person
    is not contained in personstotals
    """
    for otherperson, othertotal in personstotals:
        if othertotal != - total:
            continue
        return otherperson

def _reverseabsvalue(item, otheritem):
    """
    item, otheritem is expected as (*, number, ****)
    """
    return cmp(abs(otheritem[1]), abs(item[1]))

def heuristic(totals):
    """
    totals is expected as a dict: {person, credit}
    """
    #initialization
    debts = [
        [person, value]
        for person, value in totals.iteritems()
        if value < 0.0
    ]
    lends = [
        [person, value]
        for person, value in totals.iteritems()
        if value > 0.0
    ]
    result = [
        (person, None, 0.0)
        for person, value in totals.iteritems()
        if value == 0.0
    ]
    #loop
    while lends or debts:
        #1st step: exact matches
        #iter on a copy of lends
        for person, value in tuple(lends):
            match = _exactmmatch(debts, value)
            if match:
                result.append((match, person, value))
                lends.remove(
                    [person, value]
                )
                debts.remove(
                    [match, - value]
                )
        #continue to 2nd step?
        if not lends and not debts:
            break
        if bool(lends) != bool(debts):
            assert False, "Lends: %s, debts: %s" % (lends, debts)
        #prepare 2nd step
        debts.sort(_reverseabsvalue)
        lends.sort(_reverseabsvalue)
        #2nd step: make the biggest possible transfer
        biggestdebt = debts[0][1]
        biggestcredit = lends[0][1]
        transfer = min( - biggestdebt, biggestcredit)
        result.append((debts[0][0], lends[0][0], transfer))
        debts[0][1] += transfer
        lends[0][1] -= transfer
        #purge
        for collection in (lends, debts):
            for item in tuple(collection):
                if item[1] == 0.0:
                    collection.remove(item)

    return result
