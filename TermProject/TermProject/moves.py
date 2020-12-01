import random

def fundraise(app, state, candidate):
    #need to add cooldown for fundraising
    #can only gain money from states you are leading in
    if app.stateDict[state].demSupport > app.stateDict[state].repSupport:
        if candidate.party == 'D':
            money = app.stateDict[state].wealth
            candidate.getMoney(money)
            print(f'{candidate} earned {money}$')
        else:
            print('not your state, try something else')
            app.turns -= 1
    elif app.stateDict[state].demSupport < app.stateDict[state].repSupport:
        if candidate.party == 'R':
            money = app.stateDict[state].wealth
            candidate.getMoney(money)
        else:
            print('not your state, try something else')
            app.turns -= 1
    #no one can fundraise in tied states
    else:
        print('Not your state yet! Try something else!')
        app.turns -= 1

def poll(app, state, candidate):
    #check that player has enough money
    if candidate.money == 0:
        print('not enough money')
        app.turns -= 1
        return
    candidate.money -= 1
    #polled state is now visible
    app.stateDict[state].showing = True

def runAds(app, state, candidate):
    #check that player has enough money
    if candidate.money == 0:
        print('not enough money')
        app.turns -= 1
        return
    candidate.money -= 1
    issue = pickIssue(app, candidate)
    if issue in app.stateDict[state].hotTopics:
        if candidate.party == 'D':
            app.stateDict[state].influence += 1
        else:
            app.stateDict[state].influence -= 1
        print('Successful ad campaign!')
    else:
        print('wrong issue')
        # app.turns -= 1
    print(state, ':', app.stateDict[state].influence)

def makeSpeech(app, state, candidate):
    #check that player has enough money
    if candidate.money <= 1:
        print('not enough money')
        app.turns -= 1
        return
    candidate.money -= 2
    issue = pickIssue(app, candidate)
    if issue in app.stateDict[state].hotTopics:
        if candidate.party == 'D':
            app.stateDict[state].influence += 2
        else:
            app.stateDict[state].influence -= 2
        print('Speech was a success!')
    else:
        print('wrong issue')
        # app.turns -= 1
    print(state, ':', app.stateDict[state].influence, 'influence')

#random for now
def pickIssue(app, candidate):
    issues = list(candidate.issues)
    randIndex = random.randint(0, 4)
    return issues[randIndex]