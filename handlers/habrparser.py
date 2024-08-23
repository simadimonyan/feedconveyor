from handlers import ai

def getActualPost():
    return ai.managePost("New Post") + ""
