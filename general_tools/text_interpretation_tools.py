# -*- coding: utf-8 -*-


def condition_checker_situation_check(response):
    next_block = 'keep moving'
    for item in response["Blocks"]:
        if item["BlockType"] == "LINE":
          text = (item["Text"])
          #print(text)      
          if next_block == 'down':
              down = text
          elif next_block == 'yardline':
              yardline = text
          elif next_block == 'posession':
              posession = text
          elif next_block == 'ytg':
              ytg = text
          else:
              do_nothing = 1
         #key off the order of the blocks. the preceding block tells you the content of the next one
          if text.find('DOWN')!= -1:
              next_block = 'down'
          elif text.find('YARDLINE')!=-1:
              next_block = 'yardline'
          elif text.find('POSESSION')!= -1:
              next_block = 'posession'
          elif text.find('YARDS TO GO')!= -1:
              next_block = 'ytg'
          else:
              next_block = 'keep moving'
          
          
          
    if posession.find('1') !=-1:
        ball = 'away'
    elif posession.find('1') == -1:
        ball = 'home'
    else:
        ball = 'unknown'
        
        
    situation_json = {"down":int(down)
                    ,"yardline":float(yardline)
                    ,"yards_to_go":int(ytg)
                    ,"posession":ball
                    
                        }    
    return (situation_json)

def game_situation_check(response):
    text_list=[]
    for item in response["Blocks"]:
        if item["BlockType"] == "LINE":
          text = (item["Text"])
          text_list.append(text)
          
    return text_list
          
 
    