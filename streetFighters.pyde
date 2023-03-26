import math, pickle, json, random

def setup():
    global stage, player1, player2, imgList, gameState, scoreFileName
    global arcade, scores, scorePage, compMoveIncr
    global whichBoundary,  buttonBoundaries, buttonText, menuTextSize, buttonColours, activeButtons
    global vsComp, stageGifs, stageClickBound
    global continueGame, start, score, playerSelect, nameSelect, stageSelect, charSelect, playScreen, winEnd, gameEnd, exitRoutine
    global charFile, charPrefixes, makoto, ryu, allCharInfo, playerCharacters
    
    size(1000, 500)
    
    # SCORE VARIABLES + GET FILE INFO -----------------
    scoreFileName = 'street-fighters-scores.txt'
    scores = getScoreFileInfo( scoreFileName )
    scorePage = 0
    # ---------------
    
    
    # STAGE VARIABLES + STAGE FILE INFO -----------
    stageFileName = "allStageInfo.txt"
    stages = loadBackgroundFile( stageFileName )
    
    # animated background
    stageGifs = [ animateGif( stages[ i ][ 1 ], stages[ i ][ 0 ], width, height ) for i in range( len( stages ) ) ]
    margin = 30
    stageWidth = ( width - ( len( stages ) + 1 )*margin ) // 3
    stageHeight = 500 * stageWidth // 1000
    stageY = ( height - stageHeight ) // 2
    
    # sets stage click boundaries for player to select background
    stageClickBound = [ [ [ i*stageWidth + (i+1)*margin, stageY ],  [ i*stageWidth + (i+1)*margin + stageWidth, stageY + stageHeight] ] for i in range( len( stages ) ) ]
    
    stage = 0 # index for which stage the player chose
    # ------------------------
    
    
    # SET FONT ---------------
    arcade = createFont("Arcade_Normal.ttf", 128)
    textFont(arcade)
    #--------------------
    
    
    # LOAD CHARACTER INFORMATION ----
    allCharInfo = loadCharInfo( 'spriteInfo.txt' )
    makoto = 0 # character indexes in allCharInfo
    ryu = 1
    # -------------------
    
    
    # GAMESTATE VARIABLES ----
    start = 0 # start screen
    score = 1 # score screen
    playerSelect = 2 # computer vs player or player vs player selection
    nameSelect = 3 # enter names for player(s)
    stageSelect = 4 # selection background
    charSelect = 5 # select sprites
    playScreen = 6 # gameplay
    winEnd = 7 # win screen after end of round
    gameEnd = 8 # game end screen, decide to replay, return to start or quit
    exitRoutine = 9 # load files, exit game
    gameState = start # game starts at start scren
    # --------------
    
    
    # BUTTON BOUNDARIES AND VARIABLES
    # calculates boundaries for all buttons
    menuButtonHei = 50
    menuButtonWid = 320
    menuTextSize = 20
    menuX = width // 2
    menuY = ( height - menuButtonHei * 4 ) // 2
    menuButtons = [ [ menuX, menuY + i * menuButtonHei, menuButtonWid, menuButtonHei ] for i in range( 4 ) ]
    menuButton = [ [ width - 100, 120, 100, 70 ] ]
    whichBoundary = None
    
    continueButton = [ [ width / 2, height - 10 - 70, 200, 70 ] ]
    
    buttonBoundaries = menuButtons + continueButton + menuButton
    buttonText = [ 'RETURN TO START', 'HELP', 'SCORES', 'QUIT', 'CONTINUE', 'MENU' ]
    buttonColours = [ ( 0, 0, 0 ) for i in range( len( buttonBoundaries ) ) ]
    activeButtons = [ False for i in range( len( buttonBoundaries ) ) ]
    activeButtons[ -1 ] = True # menu button starts off on
    # ---------------
    

    
    # GAME VARIABLES -----------
    vsComp = False # checks if player is fighting against computer
    continueGame = 0 # used to check what the player wants to do after end of a game round
    compMoveIncr = 0 # holds which action computer sprite is doing
    playerCharacters = [ makoto, ryu ]
    # ----------------

    
    # LOAD + RESIZE SOME IMAGES -----------
    imgList = [[loadImage('title.png'), loadImage('textTitle.png')], 
               [loadImage('1Player.png'), loadImage('2Player.png')], 
               [loadImage('health.png')], 
               [loadImage('makotoProfile.png'), loadImage('ryuProfile.gif')]]
    
    imgList[0][1].resize(200, 100)
    imgList[2][0].resize(900, 200)
    imgList[3][0].resize(200, 200)
    imgList[3][1].resize(200, 200)

    #--------------------
        

    # CREATE PLAYER OBJECTS INITIALLY ----------------------
    player1 = Player('', 1, allCharInfo[ playerCharacters[ 0 ] ], 0, 150)
    player2 = Player('', 2, allCharInfo[ playerCharacters[ 1 ] ], 200, 150) 
    #---------------------
 
 
def draw():
    global whichBoundary, continueGame, gameState
    background(0)
    translate(width/2, height/2)
    imageMode(CENTER)

    if gameState == start:
        startScreen()
        activeButtons[ 4 ] = False
        menu()

    elif gameState == score:
        scoreScreen( scores )
        menu()
    
    elif gameState == playerSelect:
        playerSelectScreen()
        menu()
    
    elif gameState == nameSelect:
        enterNameScreen()
        menu()
        activeButtons[ 4 ] = True # continue button becomes true
        if vsComp:
            player2.name = "Computer"

        
    elif gameState == stageSelect:
        stageSelectScreen()
        activeButtons[ 4 ] = False
        menu()
        
    elif gameState == charSelect:
        characterSelectScreen()
        menu()
        
    elif gameState == playScreen:
        playingScreen()
        menu()
        
        if vsComp == True:
            # if player vs computer, use player2 as the computer
            computerMoves( player2 )

        player1.moveUpdate( player2 )
        player1.spriteUpdate( player2 )
        player1.boundCollide()
        player1.hasDied()
        
        player2.moveUpdate( player1 )
        player2.spriteUpdate( player1 )
        player2.boundCollide()
        player2.hasDied()
        
        player1.display()        
        player2.display()   
        
        if player2.won or player1.won:
            gameState = winEnd    
        
    elif gameState == winEnd:
        winScreen()
        # menu buttons turned off
        activeButtons[ : 4 ] = [ False for i in range( 4 ) ]
            
            
    elif gameState == gameEnd:
        endScreen()
        activeButtons[ : 4 ] = [ False for i in range( 4 ) ]
        
        if continueGame:
                
            if continueGame == 1: # replay same players
                gameState = playScreen
                
            elif continueGame == 2: # replay new players
                gameState = playerSelect
            
            elif continueGame == 3: # return to start screen
                gameState = start
            
            elif continueGame == 4: # exit game
                gameState = exitRoutine
            
            # insert player 1 score, or player2 score if player 2 is not computer
            if player1.won:
                insertToAllScores( [ player1.name, player1.score ], scores )

            elif player2.won and not vsComp:
                insertToAllScores( [ player2.name, player2.score ], scores )
            
            # reset gameVariables, some variables reset depending on what player presses
            setGameVariables( continueGame != 1 )            
            continueGame = 0
    
    elif gameState == exitRoutine: # save scores and exit
        loadScoreToFile( scores, scoreFileName )
        exit()

    buttonManager()
    hoverButton()
    whichBoundary = None


def loadCharInfo( filename ):
    # load character sprite info from json file
    # info includes: sprite names, # frames per animation for each sprite, animation prefixes, blueBox/vulnerable box coordinates, redBox/attack box coordinates
    with open( filename, 'r' ) as f:
        charFile = json.load( f )
    names, frames, prefixes, blueBox, redBox = 'names', 'frames', 'prefixes', 'blueBox', 'redBox'
    
    allCharInfo = []
    for name in charFile[ names ]:
        charPrefixes = [ name + prefix for prefix in charFile[ prefixes ] ]
        allCharInfo.append( [ charPrefixes, charFile[ name ][ frames ], charFile[ name ][ blueBox ], charFile[ name ][ redBox ] ] )
    
    # return list with all sprite info
    return allCharInfo


def helpScreen():
    # help screen displayed over current gameState when player hovers over help button
    # help screen disappears when player moves mouse away from help button area
    pushMatrix()
    translate( -width//2, -height//2 )
    margin = 30
    fill( 0 )
    rectMode( CORNERS )
    rect( margin, margin, width - margin, height - margin )
    rectMode( CORNER )
    
    ruleSize = 30
    ruleX = margin + ruleSize
    fill( 255 )
    textSize( ruleSize )
    textAlign( CENTER, CENTER )
    text( "RULES", width // 2, ruleX )
    
    rules = "1. In Street Fighters, the goal of the game is to attack your opponent until their health reaches 0! Every time you hit your opponent, your score increases! Points given are slightly randomized.\n\n2. In player selection screen, press 1 to play against a computer, press 2 to play against another player\n\n3. Press MENU to access buttons: Return To Start, Help, Scores, and Quit\n\n4. Scores will only save once you end a round. Pressing the X will not save your score\n\n5. To play, press space in the start screen, enter player names, choose a stage and then choose player characters\n\nPlayer 1 controls:  W - jump, A - left, D - right, Q - kick, E - punch\n\nPlayer 2 controls:  I - jump, J - left, L - right, O - kick, U - punch\n\nhover off the help button area to exit help screen"
    wordSize  = 12 
    rulesX = ruleX + 20
    textSize( wordSize )
    textAlign( LEFT, CENTER )
    text( rules, margin* 2, rulesX, width - margin*4, rulesX + 300 )
    popMatrix()


def stageSelectScreen():
    # dispalys stage/background selection screen
    global stages, stageClickBound
    pushMatrix()
    translate( -width//2, -height//2 )
    
    wordSize = 30
    textAlign( CENTER, CENTER )
    text('SELECT A STAGE\n\nPRESS SPACE TO CONTINUE', width // 2, 2*wordSize )
    textAlign( LEFT )
    imageMode( CORNER )
    selectBorder = 2
    
    stageWidth = stageClickBound[ 0 ][ 1 ][ 0 ] - stageClickBound[ 0 ][ 0 ][ 0 ]
    stageHeight = stageClickBound[ 0 ][ 1 ][ 1 ] - stageClickBound[ 0 ][ 0 ][ 1 ]
    
    for i in range( len( stageGifs ) ):
        stageOption = stageGifs[ i ].images[ 0 ].copy()
        stageOption.resize( stageWidth, 0 )
        
        # a border is drawn around the selected background
        if stage == i:
            rectMode( CORNERS )
            fill( 255, 255, 255 )
            rect( stageClickBound[ i ][ 0 ][ 0 ] - selectBorder , stageClickBound[ i ][ 0 ][ 1 ] - selectBorder, stageClickBound[ i ][ 1 ][ 0 ] + selectBorder, stageClickBound[ i ][ 1 ][ 1 ] + selectBorder)
            noFill()
            rectMode( CORNER )
            
        image( stageOption, stageClickBound[ i ][ 0 ][ 0 ] , stageClickBound[ i ][ 0 ][ 1 ] )
    
    popMatrix()


def loadBackgroundFile( filename ):
    # load information for background gif files, including background name and # of frames
    with open( filename, 'r' ) as f:
        lines = f.readlines()
    
    # each line is in the format: "stageName", # of frames
    for i in range( len ( lines ) ):
        lines[ i ] = lines[ i ].split(',')
        lines[ i ][ 1 ] = int( lines[ i ][ 1 ] )

    return lines


def computerMoves( player2 ):
    global compMoveIncr
            
    # computer telographed movements: punch, kick, walk, punch, kick, walk
    aiActions = [ 4, 5, 1, 4, 5, 1 ]
    aiActionsBools = [ 6 + i for i in aiActions ]

    # switches computer action if the current action is done/action animation is finished playing
    if player2.currentFrame == len( player2.animationList[ player2.activeAnimation ] ) - 1:
        Player.keyBools[ 6: ] = [ False for i in range( len( Player.keyBools[ 6: ] ) ) ]
        compMoveIncr += 1

        # if computer is in walking animation, walk towards player
        if aiActions[ compMoveIncr ] == 1:
            if player2.x > player1.x:
                Player.keyBools[ aiActionsBools[ compMoveIncr ] ] = True
                
            elif player2.x < player1.x:
                Player.keyBools[ aiActionsBools[ compMoveIncr ] + 2 ] = True
        else:
            Player.keyBools[ aiActionsBools[ compMoveIncr ] ] = True

    
    # restart computer telographed actions
    if compMoveIncr == len( aiActions ) - 1:
        compMoveIncr = 0
    

def buttonManager():
    global gameState, scorePage, whichBoundary, insertToScores, score
    # handles when buttons are pressed
    
    if whichBoundary == 5:
        # if menu button clicked: turn on menu buttons
        activeButtons[ : 4 ] = [ not activeButtons[ i ] for i in activeButtons[ : 4 ] ]

    elif whichBoundary == 0:
        # return to start
        gameState = start
        setGameVariables( True )
        activeButtons[ : 4 ] = [ False for i in range( 4 ) ]
        
    elif whichBoundary == 2:
        # go to scores screen
        gameState = score
        scorePage = 0
        activeButtons[ : 4 ] = [ False for i in range( 4 ) ]
        
    elif whichBoundary == 3:
        # quit game
        gameState = exitRoutine
    
    elif whichBoundary == 4:
        # continue button
        if gameState == nameSelect:
            # when names entered, continue to background selection screen
            gameState = stageSelect
    
    elif activeButtons[ 1 ]:
        # help
        # if help button hovered, display help screen
        horiCheck = mouseX > buttonBoundaries[ 1 ][ 0 ] - buttonBoundaries[ 1 ][ 2 ]/2 and mouseX < buttonBoundaries[ 1 ][ 0 ] + buttonBoundaries[ 1 ][ 2 ]/2
        vertCheck = mouseY > buttonBoundaries[ 1 ][ 1 ] - buttonBoundaries[ 1 ][ 3 ]/2 and mouseY < buttonBoundaries[ 1 ][ 1 ] + buttonBoundaries[ 1 ][ 3 ]/2
        if horiCheck and vertCheck:
            helpScreen()


def setGameVariables( notReplay ):  
    # resets game variables, only some are reset depending on what 
    # player chooses at the end of a game round  
    
    Player.keyBools = [ False for i in range( len( Player.keyBools ) ) ]
    player1.resetAttributes()
    player2.resetAttributes()
    
    # if player chooses to replay with new players, reset names
    if notReplay:
        player1.name = ''
        player2.name = ''
        
    

def menu():
    # displays menu
    global activeButtons
    pushMatrix()
    translate( -width//2, -height//2 )
    rectMode( CENTER )
    textAlign( CENTER, CENTER )
    textSize( menuTextSize )
    menu = -1
    
    # if menu buttons are active, display menu buttons
    # in this case, it only checks if the Return to start button is active to determine whether to display menu
    if activeButtons[ 0 ]:
        for i in range( 4 ):
            fill( buttonColours[ i ][ 0 ], buttonColours[ i ][ 1 ], buttonColours[ i ][ 2 ] )
            stroke( 255, 255 , 255 )
            rect( buttonBoundaries[ i ][ 0 ], buttonBoundaries[ i ][ 1 ], buttonBoundaries[ i ][ 2 ], buttonBoundaries[ i ][ 3 ] )
            
            fill( 255, 255, 255 )
            text( buttonText[ i ], buttonBoundaries[ i ][ 0 ], buttonBoundaries[ i ][ 1 ] )
    
    # displays menu button
    fill( buttonColours[ menu ][ 0 ], buttonColours[ menu ][ 1 ], buttonColours[ menu ][ 2 ] )
    stroke( 255, 255 , 255 )
    rect( buttonBoundaries[ menu ][ 0 ], buttonBoundaries[ menu ][ 1 ], buttonBoundaries[ menu ][ 2 ], buttonBoundaries[ menu ][ 3 ] )
    
    fill( 255, 255, 255 )
    text( buttonText[ menu ], buttonBoundaries[ menu ][ 0 ], buttonBoundaries[ menu ][ 1 ] )
    rectMode( CORNER )
    textAlign( LEFT, BASELINE )
    
    popMatrix()
    
    
def hoverButton():
    for i in range( len( buttonBoundaries ) ):
        horiCheck = mouseX > buttonBoundaries[ i ][ 0 ] - buttonBoundaries[ i ][ 2 ]/2 and mouseX < buttonBoundaries[ i ][ 0 ] + buttonBoundaries[ i ][ 2 ]/2
        vertCheck = mouseY > buttonBoundaries[ i ][ 1 ] - buttonBoundaries[ i ][ 3 ]/2 and mouseY < buttonBoundaries[ i ][ 1 ] + buttonBoundaries[ i ][ 3 ]/2
        
        # if button hovered, lighten the button colour
        if horiCheck and vertCheck:
            if activeButtons[ i ]:
                buttonColours[ i ] = ( 100, 100, 100 )
        
        else:
            buttonColours[ i ] = ( 0, 0, 0 )

        
                
def startScreen():
    # displays start screen
    global imgList
    image(imgList[0][0], 0, 0)
    image(imgList[0][1], 0, 60)


def playerSelectScreen():
    # display player vs computer or player vs player selection screen
    global imgList
    textAlign( CENTER )
    xmargin = 100
    ymargin = 50
    text("Enter 1 to select Player vs Computer\nor 2 for Player vs Player", 0, -height//2 + 50 )
    image(imgList[1][0], 0, 0) 
    image(imgList[1][1], 0, 100)
    textAlign( LEFT )
    
    
def enterNameScreen():
    # player name entry
    global menuTextSize, player1, player2
    continueIndex = 4
    textAlign( CENTER, CENTER )
    textSize( 20 )
    text('Hover over box to enter names', 0, -150)
    fill(30)
    rectMode( CENTER )
    rect(0, -75, 250, 50)
    textSize(10)
    fill(255)
    text("Player 1 name:" + "\n" + player1.name, 0, -85)
    
    fill(30)
    rect(0, 25, 250, 50)
    fill(255)
    text("Player 2 name:" + "\n" + player2.name, 0, 15)
        
    pushMatrix()
    translate( -width//2, -height//2)
    
    # continue button displayed
    textSize( menuTextSize )
    fill( buttonColours[ continueIndex ][ 0 ], buttonColours[ continueIndex ][ 1 ], buttonColours[ continueIndex ][ 2 ] )
    stroke( 255, 255 , 255 )
    rect( buttonBoundaries[ continueIndex ][ 0 ], buttonBoundaries[ continueIndex ][ 1 ], buttonBoundaries[ continueIndex ][ 2 ], buttonBoundaries[ continueIndex ][ 3 ] )
    
    fill( 255, 255, 255 )
    text( buttonText[ continueIndex ], buttonBoundaries[ continueIndex ][ 0 ], buttonBoundaries[ continueIndex ][ 1 ] )
    rectMode( CORNER )
    textAlign( LEFT, BASELINE )
    popMatrix()
        

def characterSelectScreen():
    # sprite selection screen
    global imgList, player1, player2, playerCharacters
    
    textSize(15)
    fill(0, 0, 255)
    textAlign( RIGHT )
    text("select {name}'s Character".format( name = player2.name ), 500 - 10, -200)    
    
    fill( 255 )
    textAlign( CENTER, CENTER )
    text('PRESS SPACE TO CONTINUE', 0, height//2 - 60 )
    
    fill(255, 0, 0)
    textAlign( LEFT )
    text("select {name}'s Character".format( name = player1.name ), -500 + 10, -200)
    
    # tint the unselected character for player 1
    gray = 130
    tintVal1, tintVal2 = 255, 255
    if playerCharacters[ 0 ] == 0: # check if  makoto
        tintVal2 = gray
    else:
        tintVal1 = gray
        
    tint( tintVal1 )
    image(imgList[3][0], -400, 0)
    tint( tintVal2 )
    image(imgList[3][1], -175, 0)
    
    # tint the unselected character for player 2

    tintVal1, tintVal2 = 255, 255
    if playerCharacters[ 1 ] == 0: # check if ryu
        tintVal2 = gray
    else:
        tintVal1 = gray
        
    pushMatrix()
    scale(-1, 1)
    tint( tintVal1 )
    image(imgList[3][0], -400, 0)
    tint( tintVal2 )
    image(imgList[3][1], -175, 0)
    popMatrix()
    
    # update player1 or player 2 character sprites if new character is selected
    if mousePressed:
        if (mouseX > width/2-500 and mouseX <width/2 -300) and (mouseY > height/2-100 and mouseY < height/2+100):
            playerCharacters[ 0 ] = makoto
            player1 = Player(player1.name, 1, allCharInfo[ playerCharacters[ 0 ] ], 0, 150)
            
        elif (mouseX > width/2-275 and mouseX <width/2 -75) and (mouseY > height/2-100 and mouseY < height/2+100):
            playerCharacters[ 0 ] = ryu
            player1 = Player(player1.name, 1, allCharInfo[ playerCharacters[ 0 ] ], 0, 150)

        elif (mouseX > width/2 +75 and mouseX < width/2 +275) and (mouseY > height/2-100 and mouseY < height/2+100):
            playerCharacters[ 1 ] = ryu
            player2 = Player(player2.name, 2, allCharInfo[ playerCharacters[ 1 ] ], 200, 150)

        elif (mouseX > width/2+300 and mouseX <width/2 + 500) and (mouseY > height/2-100 and mouseY < height/2+100):
            playerCharacters[ 1 ] = makoto
            player2 = Player(player2.name, 2, allCharInfo[ playerCharacters[ 1 ] ], 200, 150)
    
    tint( 255 )
    
def scoreScreen( origScores ):
    # displays scores 5 at a time in descending order
    global arcade
    pushMatrix()
    translate( -width//2, -height//2 )
    offset = 225
    wordSize = 20
    wordSpace = 25
    scores = origScores[ ::-1 ]
    scoresPerPage = 5
    scoresY = ( height - ( wordSize * scoresPerPage + ( scoresPerPage - 1 ) * wordSize// 2 ) ) // 2
    
    fill( 255, 255, 255 )
    textAlign( CENTER, CENTER )
    textSize( 45 )
    text( 'HIGH SCORES', width//2, 100 )
    
    textSize( wordSize )
    if scores:
        stop = scorePage * 5 + 5
        if scorePage * 5 + 5 > len( scores ):
            stop = len( scores )
        
        # displays scores 5 at a time
        for i in range( scorePage * 5, stop ):
            textAlign( RIGHT )
            text( scores[ i ][ 0 ], width - offset, scoresY + i%5 * (wordSize + wordSpace ) )
            textAlign( LEFT )
            text( scores[ i ][ 1 ], offset, scoresY + i%5 * (wordSize + wordSpace ) )
        
        # display scorepage counter
        textAlign( CENTER ) 
        textSize( wordSize * 0.75 )
        currentPage = str(scorePage + 1) + "/" + str( int( math.ceil( ( len( scores ) - 1 ) / 5 ) + 1 ) )
        text( currentPage, width // 2, height - 80 )
        text("LEFT ARROW BACK --- RIGHT ARROW NEXT", width // 2, height - 40 )
        
    else:
        # if no scores available, prompt player to play
        textAlign( CENTER )
        text( "NO SCORES RECORDED\nPLAY THE GAME!", width // 2 , height// 2 )
    
    
    popMatrix()


def playingScreen():
    # display background gif
    stageGifs[ stage ].display(0, 0)

    textAlign( CENTER, CENTER )
    wordSize = 20
    textSize( wordSize )
    
    # player health bars
    image(imgList[2][0], 0, -200)    
    noStroke()
    fill(255, 255, 0)
    rect(25, -230, player2.health, 25)
    rect(-25, -230, -player1.health, 25)
    
    # player scores
    fill(255, 0, 0)
    text(player1.score, -425, -220)
    text(player2.score, 375, -220)
    
    
    

def winScreen():
    global gameState, player1, player2, computer, vsComp
    background( 255 )
    fill( 0 )
    
    textSize( 30 )
    if player1.won:
        winner = player1
    else:
        winner = player2
        
    text( winner.name + " has won!", -300, -200 )
    text('Final score: ' + str(winner.score), -300, -100)
    winner.animationList[8][0].resize(200, 200)
    image(winner.animationList[8][0], 0, 0)
    text('press space to continue', -300, 200)


def endScreen():
    # display options for what player can do after end of a game
    # can replay w/same players or new players, return to start screen or quit
    global player1, player2, name, vsComp, computer
    
    if player1.won:
        name = player1.name
    else:
        name = player2.name
    
    x = width// 2
    y = height//2 - 20
    wordSize = 50
    pushMatrix()
    translate( -width//2, -height//2 )
    textSize( wordSize )
    fill( 255 )
    textAlign( CENTER, CENTER )
    text(name + " IS THE\nWINNER!", x, y ) 
    textSize( wordSize // 3 )
    text("\n\n\nPRESS 1 - REPLAY SAME PLAYERS\n2 - REPLAY NEW PLAYERS\n\n3 - RETURN TO START\n\n4 - QUIT GAME", x, y + wordSize*2 )
    
    popMatrix()


class animateGif:
    # creates gif objects
    def __init__(self, imageCount, imagePrefix, w, h):
        self.imageCount = imageCount
        self.images = [ 0 for i in range( self.imageCount )]
        self.frame = 0
        self.frameSpeed = 5
        self.updateCount = 0 
        for i in range(self.imageCount):
            filename = imagePrefix + ' (' + str(i + 1) + ')'+'.png'
            self.images[i] = loadImage(filename)
            self.images[i].resize(w, h)
    
    def display(self, x, y):
        if self.updateCount >= self.frameSpeed:
            self.frame = (self.frame + 1) % self.imageCount
            self.updateCount = 0

        self.updateCount += 1
        image(self.images[self.frame], x, y)

    
class Player:
    # player object
    G = 0.1 # gravity
    
    # stores which buttons have been pressed, allows buttons to be pressed simultaneously
    keyBools = [ False for i in range( 12 ) ]
    
    # provides indexes for buttons pressed
    letterKeys = [ 'w', 'a', 's', 'd', 'q', 'e', 'i', 'j', 'k', 'l', 'u', 'o' ]
    w, a, s, d, q, e, i, j, k, l, u, o = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11
        
    def __init__(self, name, player, spriteInfo, x, y):
        # spriteInfo:
        # 0 - imagePrefixes, 1 - animationFrameCounts, 2 - blueBoxes, 3 - redBoxes
        
        self.name = name
        self.action = [ False for i in range( len( spriteInfo[ 1 ]) ) ]
        # action indexes for self.action:
        # 0 idle 1 walk 2 jump 4 punch 5 kick 6 hit 7 fallen 8 win
        
        self.animationList = self.loadAnimations( spriteInfo[ 1 ], spriteInfo[ 0 ] )
        self.activeAnimation = 0
        self.currentFrame = 0 
        self.frameSpeed = 7
        self.updateCount = 0
        self.numAnimFrames = spriteInfo[ 1 ]
        self.origX = x
        self.origY = y
        self.x = x
        self.y = y
        self.speedx = 3
        self.speedy = 0
        self.player = player
        self.flip = 1
        self.health = 305
        self.blueBoxes = spriteInfo[ 2 ]
        self.redBoxes = spriteInfo[ 3 ]
        self.score = 0
        self.won = False
        self.attackCool = [ self.frameSpeed * 1 for i in range( 2 ) ] # attack cooldowns for punch and kick
        
        
    def resetAttributes( self ):
        self.action = [ False for i in range( len( self.animationList ) ) ] 
        self.activeAnimation = 0
        self.currentFrame = 0 
        self.updateCount = 0
        self.flip = 1
        self.health = 305
        self.score = 0
        self.won = False
        self.attackCool = [ self.frameSpeed * 1 for i in range( 2 ) ]
        self.x = self.origX
        self.y = self.origY
                    
                    
    def loadAnimations( self, animationFrameCounts, imagePrefixes ):
        # loads all images for each sprite animation
        animationList = []
        
        for i in range( len(imagePrefixes ) ):
            tempList = []
            
            for j in range( animationFrameCounts[ i ] ):
                imageName = imagePrefixes[ i ] + ' (' + str(j + 1) + ')'+'.png'
                tempList.append( loadImage( imageName ) )

            animationList.append( tempList )
            
        return animationList

        
    def moveUpdate( self, otherPlayer ):
        # left, right, jump, punch and kick movements for player 1 and 2
        veloY = -5
        dx = 0
        dy = 0
        self.action[ 1 ] = False
        self.action[ 3 ] = False

        if self.attackCool[0] < 50:
            self.attackCool[0]+= 1
        if self.attackCool[1] < 50:
            self.attackCool[1]+= 1
        
        if self.player == 1 and not( True in self.action[ 3: ] ):
            if Player.keyBools[ Player.a ]:
                # left
                dx = -self.speedx
                if not self.action[ 2 ]:
                    self.action[ 1 ] = True
                self.flip = 1
                    
            if Player.keyBools[ Player.d ]:
                # right
                dx = self.speedx
                if not self.action[ 2 ]:
                    self.action[ 1 ] = True
                self.flip = -1
                
            if Player.keyBools[ Player.w ] and not self.action[ 2 ]:
                self.speedy = veloY
                self.action[ 2 ] = True
                    
                
            if Player.keyBools[ Player.e ] or Player.keyBools[ Player.q ]:
                self.attack = True
                if self.attackCool[ 0 ] == 50:
                    if Player.keyBools[ Player.e ]:
                        self.action[ 4 ] = True
                        
                if self.attackCool[ 1 ] == 50:
                    if Player.keyBools[ Player.q ]:
                        self.action[ 5 ] = True
                            
                    
        elif self.player == 2 and not (True in self.action[ 3: ] ):
            if Player.keyBools[ Player.j ]:
                # left
                dx = -self.speedx
                if not self.action[ 2 ]:
                    self.action[ 1 ] = True
                self.flip = 1
                    
            if Player.keyBools[ Player.l ]:
                # right
                dx = self.speedx
                if not self.action[ 2 ]:
                    self.action[ 1 ] = True
                self.flip = -1
            if Player.keyBools[ Player.i ] and not self.action[ 2 ]:
                self.speedy = veloY
                self.action[ 2 ] = True
                    
                
            if Player.keyBools[ Player.u ] or Player.keyBools[ Player.o ]:
                self.attack = True
                if Player.keyBools[ Player.u ]:
                    if self.attackCool[ 0 ] == 50:
                        self.action[ 4 ] = True
                
                if Player.keyBools[ Player.o ]:
                    if self.attackCool[ 1 ] == 50:
                        self.action[ 5 ] = True

        
        self.speedy += Player.G
        dy = self.speedy
        
        self.x += dx
        self.y += dy                
        
    def boundCollide( self ):
        # left, right and lowerbound collision detection
        if self.y > 150:
            self.y = 150
            self.speedy = 0
            self.action[ 2 ] = False
            
        if self.x > width // 2:
            self.x = width // 2
            
        elif self.x < -width // 2:
            self.x = -width // 2
            
            
    def spriteUpdate( self, otherPlayer ):
        # updates sprites active/current animation
        global gameState 
        if self.action[ 1 ]: # walk
            self.updateAction( 1 )
            
        elif self.action[ 2 ]: # jump
            self.updateAction( 2 )
        
        elif self.action[ 4 ]: # punch
            self.updateAction( 4 )
            
            # if punch animation is finished, turn off punch animaiton and reset attack cooldown
            if self.currentFrame == (len(self.animationList[4])-1):
                self.action[ 4 ] = False
                self.attackCool[0] = 0
            
            # handles attack related events
            self.attackOther( otherPlayer )

        
        elif self.action[ 5 ] : # kick
            self.updateAction( 5 )
            
            # if kick animation finished, turn off kick aniamtion
            if self.currentFrame == (len(self.animationList[5])-1):
                self.action[ 5 ] = False
                self.attackCool[1] = 0
                
            self.attackOther( otherPlayer )

                
        elif self.action[ 6 ]: # attacked animation
            self.updateAction( 6 )
            if self.currentFrame == len( self.animationList[ 6 ] ) - 1:
                self.action[ 6 ] = False
                
        elif self.action[7]: # fallen/defeated animation
            self.updateAction( 7 ) 
            
            # once player's defeated animation is complete, otherplayer has won the round
            if self.currentFrame == (len(self.animationList[7])-1):
                otherPlayer.won = True
                self.action[7] = False
                
        else: # if no action active, return to idle
            self.updateAction( 0 )
        
        # updates player's animation frame
        # will only update if the updatecount is equal to framespeed
        # allows us to manually set animation speed of sprites
        if self.updateCount >= self.frameSpeed: 
            self.currentFrame = ( self.currentFrame + 1 ) % len( self.animationList[ self.activeAnimation ] )
            self.updateCount = 0
            
        self.updateCount += 1
    
    
    def hasDied(self):
        if self.health <= 0:
            self.health = 0
            self.action[ 7 ] = True # turns on defeated/fallen animation
    
    
    # if the newanimation to update with is different from the current animation,
    # reset the frame count and set the current animation to the new animation
    def updateAction( self, newAnimation ):
        if newAnimation != self.activeAnimation:
            self.activeAnimation = newAnimation
            self.currentFrame = 0
            
    # displays player sprite
    def display( self ):
        currentImage = self.animationList[ self.activeAnimation ][ self.currentFrame ]
        pushMatrix()
        scale( self.flip, 1 )
        image( currentImage, self.flip * self.x, self.y )
        popMatrix()
        
        
    def attackOther( self, otherPlayer ):
        # gets the frame when the attack is fully extended
        attackFrame = self.redBoxes[ self.activeAnimation ][ 1 ]
        
        # if on the attack frame and otherPlayer is hit
        if self.currentFrame == attackFrame and self.isCollided( otherPlayer ):
            otherPlayer.action[ 6 ] = True # turn on otherplyer's hit animation
            otherPlayer.x += -10 * self.flip # push otherplayer back
            self.score += random.randint(50, 100) # a random amt of points allotted for each hit
            otherPlayer.health -= 20
                
   
    def isCollided( self, otherPlayer ): # checks if player has collided w/ other player by comparing player's hitbox to otherplayer's vulnerable boxes
        # other players vulnerable boxes
        oHurtBoxes = otherPlayer.blueBoxes[ otherPlayer.activeAnimation ] 
        
        # player's current attack boxes
        pHitBox = self.redBoxes[ self.activeAnimation ][ 0 ]
        
        # flips player's attack box based on flip status
        if self.flip == 1:
            playerBox = [ self.x + pHitBox[ 0 ], self.y + pHitBox[ 1 ], pHitBox[ 2 ], pHitBox[ 3 ] ]
        else:
            playerBox = [ self.x + pHitBox[ 0 ] * self.flip - pHitBox[ 2 ], self.y + pHitBox[ 1 ], pHitBox[ 2 ], pHitBox[ 3 ] ]
        
        for hurtBox in oHurtBoxes:
            # flip otherplayer's vulnerable/hurt box based on flip status
            if otherPlayer.flip == 1:
                otherBox = [ otherPlayer.x + hurtBox[ 0 ], otherPlayer.y + hurtBox[ 1 ], hurtBox[ 2 ], hurtBox [ 3 ] ]
            else:
                otherBox = [ otherPlayer.x + hurtBox[ 0 ] * otherPlayer.flip - hurtBox[ 2 ], otherPlayer.y + hurtBox[ 1 ], hurtBox[ 2 ], hurtBox [ 3 ] ]

            if self.boxCollision( playerBox, otherBox ):
                return True

        return False
        
                
    def boxCollision(self, b1, b2 ):
        # b1 and b2 are lists, format: [ x, y, w, h ]
        x, y, w, h = 0, 1, 2 ,3
        horiCheck = b1[ x ] + b1[ w ] > b2[ x ] and b1[ x ] < b2[ x ] + b2[ w ]
        vertCheck = b1[ y ] + b1[ h ] > b2[ y ] and b1[ y ] < b2[ y ] + b2[ h ]
                
        return horiCheck and vertCheck
            
                    
def binarySearchInsert( startList, want ):
    top = 0
    bottom = len(startList) - 1 
    where = (top + bottom)//2
    
    while top <= bottom:
        if startList[ where ][ 1 ] == want:
            return where
    
        elif want > startList[ where ][ 1 ]:
            top = where + 1
        
        else:
            bottom = where - 1
        
        where = (top + bottom)//2
    
    return top

def insertToAllScores( newScore, allScores ): # inserts a score into all scores
    if allScores == []:
        allScores.append( newScore )
    else:
        nameIndex = existName( newScore[ 0 ], allScores )
        if nameIndex != None:
            allScores[ nameIndex ][ 1 ] = max( newScore[ 1 ], allScores[ nameIndex ][ 1 ] )  
        else:
            correctIndex = binarySearchInsert( allScores, newScore[ 1 ] )
            allScores.insert( correctIndex, newScore )    



def existName( name, allScores ): # checks if a name already exists in allscores
    for score in allScores:
        if name in score:
            return allScores.index( name )
    return None


def loadScoreToFile( allScores, filename  ):
    with open( filename, "wb" ) as f:
        pickle.dump( allScores, f )
    
    
def getScoreFileInfo( filename ):
    # tries to open filename and unpickle scores
    try:
        with open( filename, "rb") as f:
            allScores = pickle.load( f )
            
    # if no score file, create allScores list and file
    except:
        f = open( filename, "wb" )
        f.close()
        allScores = []

    return allScores 


def mouseReleased():
    global whichBoundary, buttonBoundaries, activeButtons, stageGifs, stage
    
    # checks for if buttons have been pressed, returns index of pressed button
    for i in range( len( buttonBoundaries ) ):
        horiCheck = mouseX > buttonBoundaries[ i ][ 0 ] - buttonBoundaries[ i ][ 2 ]/2 and mouseX < buttonBoundaries[ i ][ 0 ] + buttonBoundaries[ i ][ 2 ]/2
        vertCheck = mouseY > buttonBoundaries[ i ][ 1 ] - buttonBoundaries[ i ][ 3 ]/2 and mouseY < buttonBoundaries[ i ][ 1 ] + buttonBoundaries[ i ][ 3 ]/2
        if activeButtons[ i ] and horiCheck and vertCheck:
            whichBoundary = i
            return
    
    # for background selection, returns which background has been selected
    if gameState == stageSelect:
        for i in range( len( stageClickBound ) ):
            horiCheck = mouseX > stageClickBound[ i ][ 0 ][ 0 ] and mouseX < stageClickBound[ i ][ 1 ][ 0 ]
            vertCheck = mouseY > stageClickBound[ i ][ 0 ][ 1 ] and mouseY < stageClickBound[ i ][ 1 ][ 1 ]
            
            if horiCheck and vertCheck:
                stage = i
                return
            

def keyPressed():
    global gameState, vsComp, player1, player2

    # name entry
    # deletes characters when backspace pressed, adds characters if name is not greater than 11 characters
    # does not add backspace or tab to name
    
    notAllowed = [ "\n", "\t" ]
    maxCharLen = 11
    
    if gameState == nameSelect:
        if (mouseX > width/2-100 and mouseX < width/2+250) and (mouseY > height/2 -100 and mouseY < height/2 -50):
            if key == '\b':
                player1.name = player1.name[ :-1]
                        
            elif len(player1.name) < maxCharLen and key not in notAllowed:
                try:
                    
                    player1.name += key
                except:
                    pass
                    
        if not vsComp and (mouseX > width/2-100 and mouseX < width/2+250) and (mouseY > height/2 and mouseY < height/2+50):
            if key == '\b':
                player2.name = player2.name[ :-1]
                        
            elif len(player2.name) < maxCharLen and key not in notAllowed:
                try:
                    player2.name += key
                except:
                    pass
    
    # if player controls are pressed, turn them on in Player.keyBools
    # using Player.keyBools list allows keys to be pressed simultaneously
    elif gameState == playScreen:
        if key in Player.letterKeys[ : 6 ]:
            Player.keyBools[ Player.letterKeys.index( key ) ] = True
        
        # only register player2 keys if player2 is not computer
        if not vsComp and key in Player.letterKeys[ 6 : ]:
            Player.keyBools[ Player.letterKeys.index( key ) ] = True
        

def keyReleased():
    global scorePage, gameState, vsComp, continueGame
    
    if gameState == start:
        if key == ' ':
            gameState = playerSelect
    
    elif gameState == playerSelect:
        if key == '1':
            gameState = nameSelect
            activeButtons[ 4 ] = True # turn on continue button
            vsComp = True
            
        if key == '2':
            gameState = nameSelect
            activeButtons[ 4 ] = True # turn on continue button
            vsComp = False
            
    elif gameState == stageSelect:
        if key == ' ':
            gameState = charSelect
    
    elif gameState == charSelect:
        if key == ' ':
            gameState = playScreen
    
    elif gameState == playScreen:
        # if control keys are released, turn off corresponding bools in Player.keyBools
        # this allows us to check if multiple keys have been pressed/released
        if key in Player.letterKeys[ : 6 ]:
            Player.keyBools[ Player.letterKeys.index( key ) ] = False
        
        # only register player2 keys if not computer
        if not vsComp and key in Player.letterKeys[ 6 : ]:
            Player.keyBools[ Player.letterKeys.index( key ) ] = False

            
    elif gameState == score:
        # left arrow to decrease score page, right arrow to increase
        if key == CODED:
            if keyCode == RIGHT:
                # only increase score page if not on last page
                if scorePage < math.ceil( ( len( scores ) - 1 ) / 5 ):
                    scorePage += 1
                
            elif keyCode == LEFT:
                # only decrease score page if not on first page
                if scorePage > 0:
                    scorePage -= 1
                    
    elif gameState == playScreen:
        if key == ' ':
            gameState = winEnd
    
    elif gameState == winEnd:
        if key == ' ':
            gameState = gameEnd
    
            
    elif gameState == gameEnd:
        # checks what player wants to do at end of round 
        # 1 - replay same players 2 - replay new players
        # 3 - return to start 4 - quit game
        if key == '1' or key == '2' or key == '3' or key == '4':
            continueGame = int( key )                            
            
        
