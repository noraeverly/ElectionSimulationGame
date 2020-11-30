
def fundraise(app, state, candidate):
    #need to make this so you can only get money from states you are winning
    #also add cooldown for fundraising
    money = app.stateDict[state].wealth
    candidate.getMoney(money)

def poll(app, state, candidate):
    if candidate.money == 0:
        print('not enough money')
        return
    candidate.money -= 1
    app.stateDict[state].showing = True

def runAds(app, state, candidate):
    if candidate.money == 0:
        print('not enough money')
        return
    candidate.money -= 1
    issue = chooseIssue(app, candidate)
    if issue in app.stateDict[state].hotTopics:
        if candidate.party == 'D':
            app.stateDict[state].influence += 1
        else:
            app.stateDict[state].influence -= 1
    else:
        print('wrong issue')
    print(state, ':', app.stateDict[state].influence)

def makeSpeech(app, state, candidate):
    if candidate.money <= 1:
        print('not enough money')
        return
    candidate.money -= 2
    issue = chooseIssue(app, candidate)
    if issue in app.stateDict[state].hotTopics:
        if candidate.party == 'D':
            app.stateDict[state].influence += 2
        else:
            app.stateDict[state].influence -= 2
    else:
        print('wrong issue')
    print(state, ':', app.stateDict[state].influence)

def chooseIssue(app, candidate):
    return 'D'