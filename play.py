import tkinter as tk
from p_types import PokemonType
from moves import Move
from pokemon import Pokemon
from battle import Battle

class Game:
    def __init__(self):
        self.battle_num = 0
        self.max_battles = 3
        self.current_battle = None

    def startBattle(self):
        self.battle_num += 1
        self.current_battle = Battle(self.battle_num, self.max_battles)

        return self.current_battle

class UI:
    def __init__(self, game):
        self.game = game
        self.messages = {
            "start_message": """Welcome to the Pokemon Battle Tower!
In order to become the Battle Tower Champion, you must win {} battles in a row.
Becoming the champion will not be easy, because every battle will be harder than last one.""".format(self.game.max_battles),
            "choose_message": """Battle #{}!
Please Select 3-6 pokemons as partners.
""",
            "battle_won": "You won the battle! Next battle will start in a few seconds.",
            "lose": "You lost the battle... Maybe you'll win next time :)",
            "champ": "You are now the Pokemon Battle Tower Champion!",
        }

class GUI(UI):
    def __init__(self, game):
        UI.__init__(self, game)
        # main window
        self.top = tk.Tk()
        self.top.minsize(500, 400)
        self.top.resizable(0,0)
        self.top.title("Pokemon Battle Tower")
        self.top.iconbitmap("icon.ico")

        # first/choose screen with tower background. use self.tower_img to make the image stay in memory!
        self.start_canvas = tk.Canvas(self.top, bg="#ddd")
        self.start_canvas.pack(fill = tk.BOTH, expand = True)
        self.tower_img = tk.PhotoImage(file = "./images/tower.png")
        self.start_canvas.create_image(-211, 0, anchor = tk.NW, image = self.tower_img)

        # first screen button and text
        button = tk.Button(self.start_canvas, text = "START GAME", fg = "blue", command = self.chooseScreen)
        button.pack(side = tk.BOTTOM, pady = 20)
        label = tk.Message(self.start_canvas, text = self.messages["start_message"], bg="#eee", width = 450, bd = 10)
        label.pack(side = tk.BOTTOM, pady = 0)

        # mark start_canvas as current_scr
        self.current_scr = self.start_canvas

        # battle_frame to be used later
        self.battle_frame = tk.Frame(self.top, bd = 0)
        self.battle_canvas = tk.Canvas(self.battle_frame, height = 280, bg="#fff")
        self.battle_canvas.pack(fill = tk.X, expand = False, side = tk.TOP)
        self.bg_img = [tk.PhotoImage(file = "./images/bg_{}.png".format(k)) for k in [1,2,3]]
        self.current_battle_back = None
        moves_and_messages = tk.Frame(self.battle_frame, bg = "#000")
        moves_and_messages.pack(fill = tk.BOTH, expand = True, padx = 2, pady = 2)

        # battle_frames: install messages
        message_block = tk.Frame(moves_and_messages, bg = "#ddd", width = 150)
        message_block.pack(fill = tk.Y, expand = False, pady = 2, padx = (2, 0), side = tk.RIGHT)
        # contain messages so they won't expand
        text_container = tk.Frame(message_block, bd = 0, width = 150)
        text_container.pack(side = tk.LEFT, fill = tk.BOTH, expand = True)
        text_container.grid_propagate(False)
        text_container.grid_rowconfigure(0, weight=1)
        text_container.grid_columnconfigure(0, weight=1)
        self.message_text = tk.Text(text_container, bg = "#ddd", relief = tk.FLAT, wrap = tk.WORD, font = ("Arial", 8))
        self.message_text.tag_configure('bold', font=('Arial', 8, 'bold'))
        self.message_text.grid(row=0, column=0, sticky="nsew")
        # scrollbar for messages
        message_scroll = tk.Scrollbar(message_block)
        self.message_text.configure(yscrollcommand = message_scroll.set, state = tk.DISABLED)
        message_scroll.configure(command = self.message_text.yview)
        message_scroll.pack(side = tk.RIGHT, fill = tk.Y)

        # battle_frames: install moves
        moves_block = tk.Frame(moves_and_messages, bg = "#ddd")
        moves_block.pack(fill = tk.BOTH, expand = True, pady = 2, padx = 0, side = tk.LEFT)
        self.moves = []
        self.selected_move = tk.IntVar()
        for i in range(4):
            self.moves.append( tk.Radiobutton(moves_block, text = " - ", value = i, variable = self.selected_move, state = tk.DISABLED, width = 18, height = 2, anchor = tk.W, bg = "#ddd", justify = tk.LEFT) )
            self.moves[i].grid(row = i%2, column = int(i/2))
        self.confirm_button = tk.Button(moves_block, text = "Go!", anchor = tk.S, state = tk.DISABLED, command = self.confirmMove)
        self.confirm_button.grid(row = 0, column = 2, rowspan = 2, padx = (5, 10))
        moves_block.grid_rowconfigure(0, weight=1)
        moves_block.grid_rowconfigure(1, weight=1)
        moves_block.grid_columnconfigure(0, weight=1)
        moves_block.grid_columnconfigure(1, weight=1)
        moves_block.grid_columnconfigure(2, weight=0)

        # battle_frames: pokemon details
        self.partner_details = tk.StringVar()
        self.enemy_details = tk.StringVar()
        details = [{'x': 20, 'y': 120, 'var': self.partner_details}, {'x': 370, 'y': 20, 'var': self.enemy_details}]
        for d in details:
            details_frame = tk.LabelFrame(self.battle_canvas, bg = "#000", relief = tk.FLAT)
            details_frame.place(x = d['x'], y = d['y'])
            details_label = tk.Label(details_frame, textvariable = d['var'], bg = "#f9f9fa", width = 18, anchor = tk.CENTER)
            details_label.pack(expand = True, side = tk.LEFT)

        # battle_frames: battle animations set up
        self.animation = dict()
        self.animation["partner"] = {'ref': None, 'img': None, 'allow': False, 'func': None}
        self.animation["enemy"] = {'ref': None, 'img': None, 'allow': False, 'func': None}

    def chooseScreen(self):
        battle = self.game.startBattle()

        # we came from a battle, just pack_forget the screen so it can be re-used later
        if self.current_scr != self.start_canvas:
            self.current_scr.pack_forget()
            self.start_canvas.pack(fill = tk.BOTH, expand = True)

        # get the first screen, destroy everything except for background...
        self.current_scr = self.start_canvas
        for child in self.current_scr.winfo_children():
            child.destroy()

        # just a button
        button = tk.Button(self.start_canvas, text = "CONFIRM SELECTION", fg = "blue")
        button.pack(side = tk.BOTTOM, pady = 20)

        # frame for message and pokemon options
        frame = tk.Frame(self.start_canvas, bg="#eee", width = 450, bd = 10)
        frame.pack(side = tk.BOTTOM, pady = 0)

        # put message in top row of frame
        message = self.messages["choose_message"].format(self.game.battle_num)
        label = tk.Message(frame, text = message, bg="#eee", width = 400, anchor = tk.NW)
        label.grid(row = 0, column = 0, columnspan = 3)
        
        # get pokemon options:
        options = battle.availableList()

        # put pokemon options in frame
        menus = []
        intVars = []
        for i in range(6):
            intVars.append(tk.IntVar(value = -1))
            txt = tk.StringVar(value = "Pokemon #{}".format(i+1))
            menus.append( tk.Menubutton(frame, textvariable = txt, width = 15, relief = tk.GROOVE, bg="#fff") )
            menus[i].grid(row = int(i/3)+1, column = i%3, padx = 1)
            menus[i].menu = tk.Menu(menus[i], tearoff = 0)
            menus[i]['menu'] = menus[i].menu
            for j in range(len(options)):
                menus[i].menu.add_radiobutton(label = options[j]['name'], value = j, variable = intVars[i], command = lambda n = i, k=j, t = txt: t.set(options[k]['name']))

        # check if player chose enough pokemons, if so start the battle
        def checkOptions():
            selection = [options[var.get()] for var in intVars if var.get() > -1]
            partner = battle.selectPartners(selection)
            if partner == None:
                from tkinter.messagebox import showwarning
                showwarning("Not Enough Pokemons", "Please choose at least 3 pokemons for the battle.")
            else:
                self.startBattle(partner)

        button.configure(command = checkOptions)

    def startBattle(self, partner):
        # forget last screen, mark battle_frame as current
        self.current_scr.pack_forget()
        self.battle_frame.pack(fill = tk.BOTH, expand = True)
        self.current_scr = self.battle_frame
        
        # delete bg of last battle if there is one, and insert the new background
        if self.current_battle_back != None:
            self.battle_canvas.delete(self.current_battle_back)
        bg_y_cord = -140 if self.game.battle_num != 2 else -80
        self.current_battle_back = self.battle_canvas.create_image(-200, bg_y_cord, anchor = tk.NW, image = self.bg_img[self.game.battle_num - 1])

        # clear details
        for d in [self.partner_details, self.enemy_details]:
            d.set("")

        # clear messages
        self.message_text.configure(state = tk.NORMAL)
        self.message_text.delete(1.0, tk.END)
        self.message_text.configure(state = tk.DISABLED)

        # clear animations
        for pl in ["enemy", "partner"]:
            if self.animation[pl]['ref'] != None:
                self.animation[pl]['allow'] = False
                self.battle_canvas.after_cancel(self.animation[pl]['func'])
                self.animation[pl]['ref'] = None
                self.battle_canvas.delete(self.animation[pl]['img'])

        # get the pokemons
        self.setPokemon(partner)
        enemy = self.game.current_battle.selectEnemies()
        self.setPokemon(enemy)

        return self.turn()

    def battleMessage(self, message, bold = False):
        # print the message
        self.message_text.configure(state = tk.NORMAL)
        if bold:
            self.message_text.insert(tk.END, message + "\n", "bold")
        else:
            self.message_text.insert(tk.END, message + "\n")
        self.message_text.configure(state = tk.DISABLED)

        # scroll messages down
        self.message_text.yview(tk.END)

    def load_gif_frames(self, pname, is_partner):
        i = 0
        img = []
        side = "back" if is_partner else "front"
        while True:
            try:
                img.append(tk.PhotoImage(file = "./images/{}/{}.gif".format(side, pname.lower()), format = "gif -index {}".format(i)))
                i += 1
            except:
                break
        
        return img

    def setPokemon(self, pokemon):
        is_partner = not pokemon.isEnemy()
        self.battleMessage("{} sent out {}!".format("You" if is_partner else "Enemy", pokemon.getName()), True)
        if is_partner:
            self.battleMessage(pokemon.printStats())

        det = self.partner_details if is_partner else self.enemy_details
        det.set("{} (HP: {}%)\n{}".format(pokemon.getName(), 100, "/".join(format(tp.getName()) for tp in pokemon.getTypes())))

        pl = "partner" if is_partner else "enemy"

        img = self.load_gif_frames(pokemon.getName(), is_partner)
        self.animation[pl]['ref'] = img[0]
        img_width = img[0].width()
        cord_y, x_start, x_end, img_anchor = (260, -img_width, 70, tk.SW) if is_partner else (180, 500+img_width, 500+img_width-180, tk.SE)
        self.animation[pl]['img'] = self.battle_canvas.create_image(x_start, cord_y, anchor = img_anchor, image = self.animation[pl]['ref'])

        # go through all frames of animation in a loop
        def animate():
            if self.animation[pl]['allow'] == True:
                # get next frame
                selected_img = img.pop(0)
                img.append(selected_img)

                # put the next frame
                ready = self.battle_canvas.create_image(x_end, cord_y, anchor = img_anchor, image = selected_img)

                # delete previous frame
                self.battle_canvas.delete(self.animation[pl]['img'])
                self.animation[pl]['img'] = ready
                self.animation[pl]['ref'] = selected_img

                # return here in 20 ms
                self.animation[pl]['func'] = self.battle_canvas.after(20, animate)

        # animate pokemon into the screen, then turn animate() on
        def entrance(i):
            self.battle_canvas.delete(self.animation[pl]['img'])
            selected_img = img.pop(0)
            img.append(selected_img)
            self.animation[pl]['ref'] = selected_img
            alpha = ((30-i)/30)*x_start + (i/30)*x_end
            self.animation[pl]['img'] = self.battle_canvas.create_image(alpha, cord_y, anchor = img_anchor, image = self.animation[pl]['ref'])
            if i < 30:
                self.battle_canvas.after(15, entrance, i+1)
            if i == 30:
                # entrance sequence is done, turn on animate()
                self.animation[pl]['allow'] = True
                animate()
        entrance(0)

        self.battleMessage("")

    def faint(self, is_partner):
        pl = "partner" if is_partner else "enemy"

        # turn current animation off
        self.animation[pl]['allow'] = False
        self.battle_canvas.after_cancel(self.animation[pl]['func'])
        
        # clear fainted pokemon's details
        details = self.partner_details if is_partner else self.enemy_details
        details.set("")

        # animate fainting
        img = self.animation[pl]['img']
        def faintAnimate(i):
            self.battle_canvas.move(img, 0, 2)
            self.top.update()
            if i < 30:
                self.battle_canvas.after(10, faintAnimate, i+1)
            else:
                self.battle_canvas.delete(img)
        faintAnimate(0)

    def turn(self):
        battle = self.game.current_battle
        moves = battle.possibleMoves()

        for i in range(len(moves)):
            move_text = "{} (PP:{})\n{}, {}".format(moves[i].getName(), moves[i].getPP(), moves[i].getType().getName(), moves[i].getCategory() )
            self.moves[i].configure(state = tk.NORMAL, text = move_text)
        
        self.confirm_button.configure(state = tk.NORMAL)

    def confirmMove(self):
        battle = self.game.current_battle
        for move in self.moves:
            move.configure(state = tk.DISABLED, text = " - ")
        self.confirm_button.configure(state = tk.DISABLED)

        moves = battle.possibleMoves()
        messages = battle.doTurn(moves[ self.selected_move.get() ])
        for message in messages:
            self.battleMessage(message)

        self.battleMessage("")

        # reset selected move if needed
        if moves[ self.selected_move.get() ].getPP() == 0:
            self.selected_move.set(0)
        
        # wait 500 ms between turns
        time_to_wait = 500
        for pokemon in battle.getPokemons():
            det = self.enemy_details if pokemon.isEnemy() else self.partner_details
            det.set("{} (HP: {}%)\n{}".format(pokemon.getName(), pokemon.getHPPercentage(), "/".join(format(tp.getName()) for tp in pokemon.getTypes())))

            # a pokemon fainted, wait 2 seconds (time to faint and switch in animations)
            if pokemon.getHP() == 0:
                time_to_wait = 2000

        if battle.switchFainted(self.faint, self.switchIn) == False:
            if battle.playerWin():
                if self.game.battle_num == self.game.max_battles:
                    self.battleMessage(self.messages["champ"], True)
                else:
                    self.battleMessage(self.messages["battle_won"], True)
                    self.top.after(4000, lambda: self.chooseScreen())
            else:
                self.battleMessage(self.messages["lose"], True)
        else:
            self.top.after(time_to_wait, lambda: self.turn())

        
    def switchIn(self, pokemon, left):

        self.battleMessage("{} pokemon{} left in {} group.".format(left, "s" if left > 1 else "", "enemy's" if pokemon.isEnemy() else "your"))
        self.battleMessage("")

        # wait for fainting pokemon to disappear
        self.top.after(500, lambda: self.setPokemon(pokemon))
        
        
        

    def waitForInput(self):
        self.top.mainloop()

if __name__ == "__main__":

    import ctypes

    myappid = 'maorlevy.pokemontower' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    game = Game()
    ui = GUI(game)
    ui.waitForInput()