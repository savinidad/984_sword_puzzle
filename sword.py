print('hi dad')

class Puz():
    """Top puzzle, solver and pieces.
The pieces and the pyramid are defined by their tits.  Each has 3 columns
of tits and 8 rows.  When all these pieces are defined, the solver tries to 
lower the two half-cylinder pieces into the pyramid by twisting the pair and 
moving each half up and down while obeying the stops encountered.

The solver keeps track of each state visited and the path it took to get 
there.  If a shorter path is found it will be the new path to that state.

The solver will explore depth-first in the downward direction for each piece,
and will not yet bother with guaranteeing the shortest solution.

Piece definition:
[[1, 1, 1],
 [0, 0, 0],
 [0, 0, 0],
 [1, 1, 1],
 [1, 0, 0],
 [0, 0, 0],
 [1, 0, 1],
 [0, 0, 0],
 [1, 1, 0],
 [0, 0, 1]]

 And the pyramid is similar, but with 6 columns.

 The solver will move the pices in the smallest increments:
 - piece 0 up/down
 - piecd 1 up/down
 - cyl twist 0-5

 The pieces each have a state based on rotation and vert.  I'll define 
 the 0 state as both pieces all the way inserted, flush with the 
 pyramid.  The solver will pull it out.

 How to describe each state of the puzzle with a unique string?
 The state is just the position of the corner of each piece, four
 characters will do.  a0d2 for example has piece 0 at level 0 rotation
 a and piece 1 at 2 d.  The starting state has the seam horizontal and 
 both pieces at level 0.  I'll name 12:00 rotation a, meaning the center of 
 a piece is at 12:00, so the starting state is a0d0.

 How about each move?  How can I shorthand each move?  One character will
 suffice:  + and - for rotations, f, F, r, R for front and rear down or up.
 Because the pieces are so difficult to distinguish, and because the 
 geometry of the puzzle dictates that there will always be a front and a 
 rear piece.  Later, when putting it back together, I'll have to distinguish
 pieces to get started.  

 The solver will track pieces 0 and 1, and some translation will be applied
 when communicating moves to the human who can't distinguish pieces but can
 distinguish front and rear pieces.

 Pull the sword found with 40 moves:
 40  path:ARRRRABRARBBrararbrAARABRBBBrbarbrAAARBB [6, 6, 2] in 131 tries
 Put it back is different
 36  path:abbraaRBRARbbrabraaaRABRARARbbraraba       [0, 0, 4]  =>  success in 83 tries
    """
    def __init__(self) -> None:
        self.piece = [
            [
                [1, 1, 1], # 0
                [0, 0, 0],
                [0, 0, 0], # 2
                [1, 1, 1],
                [1, 0, 0], # 4
                [0, 0, 0],
                [0, 1, 0], # 6
                [0, 0, 0],
                [0, 0, 1], # 8
                [1, 1, 0]
            ],
            [
                [1, 1, 1], #
                [0, 0, 0],
                [0, 0, 0],
                [1, 1, 1],
                [0, 0, 1], #
                [0, 0, 0],
                [1, 0, 1],
                [0, 0, 0],
                [0, 1, 1], #
                [1, 0, 0]
            ],
        ]
        self.pyramid = [
            [0, 0, 0, 0, 0, 0], # 0
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0], # 2
            [0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 0], # 4
            [1, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0], # 6
            [0, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0], # 8 
            [0, 0, 0, 0, 0, 0], # 9
        ]
        # this vector represents, piece 0 height, piece 1 height, rotation
        #self.state = [0, 2, 3]
        # when I used this non-ideal move sequence, tries went from 131 to 143 ~10% is all
        self.move = [
            [-1, 0, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1],
            [1, 0, 0], [0, 1, 0]
        ]
        self.move_ch = "abRrAB" # character representatin of move
        self.state =       [6, 6, 2]
        self.final_state = [0, 0, 0]
        #self.move = [
            #[1, 0, 0], [0, 1, 0], [0, 0, 1], [0, 0, -1],
            #[-1, 0, 0], [0, -1, 0]
        #]
        #self.move_ch = "ABRrab" # character representatin of move
        # multiple paths to same state are possible, I'll keep track of
        # the shortest path
        self.been_there = {"%s" % (self.state):""}
        self.tries = 0

    def is_clear(self):
        """True if state is collision-free, else False"""
        # verify that the a and b pieces are within their limit
        if abs(self.state[0] - self.state[1]) > 2:
            print("a-b > 2")
            return False
        # verify the a and b pieces are not negative
        if self.state[0] < 0 or self.state[1] < 0:
            print("a or b negative")
            return False
        # verify the a and b pieces are not beyond pyramid top
        if self.state[0] > 8 or self.state[1] > 8:
            print("a or b beyond")
            return False
        # traverse the pieces and pyramid, looking for collisions
        for piece_n in range(2):
            for row in range(10):
                # if the row is outside the puzzle, nvm
                pyramid_row = row - self.state[piece_n]
                if pyramid_row < 0:
                    continue
                for col in range(3):
                    try:
                        # determine interference
                        piece_tit = self.piece[piece_n][row][col]
                        pyramid_tit = self.pyramid[pyramid_row][(col + piece_n*3 + self.state[2])%6]
                        if piece_tit & pyramid_tit:
                            print("collision, n:%d row:%d col:%d  %s" % (piece_n, row, col, self.state))
                            return False
                    except IndexError:
                        continue
        return True # got through all the tits without a collision

    def try_this(self, level, path):
        self.tries += 1
        """Recursive search."""
        print("%2d  %15s  %14s  =>  " % (level, path, self.state), end="") # todo debug
        # limit the level to find a shorter solution
        if level > 40:
            print("too many levels")
            return False
        #if self.state[0]>=9 and self.state[1]>=9:
        if self.state[0]==self.final_state[0] and self.state[1]==self.final_state[1]:
            print("success in %d tries" % (self.tries))
            return path # this means success, False means otherwise
        if not self.is_clear():
            return False # collision
        for move_n in range(6):
            # apply move
            self.state = [a+b for a, b in zip(self.state, self.move[move_n])]
            self.state[2] = self.state[2]%6 # prevent very unlikely oscillation
            # check to see if we've been here
            if ("%s" % (self.state) in self.been_there):
                self.state = [a-b for a, b in zip(self.state, self.move[move_n])]
                self.state[2] = self.state[2]%6 # prevent very unlikely oscillation
                continue
            else:
                self.been_there.update({"%s" % (self.state):path})
            print("ok")
            success = self.try_this(level+1, path + self.move_ch[move_n])
            if success:
                return success
            # back out the move, it didn't lead to success
            self.state = [a-b for a, b in zip(self.state, self.move[move_n])]
        print("no way forward")
        return False # all ways forward failed

p = Puz()
p.try_this(0, "path:")
print("%d tries" % (p.tries))