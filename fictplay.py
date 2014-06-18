from __future__ import division
import numpy as np


class NormalFormGame_2P:
    players = [0, 1]

    def __init__(self, payoffs):
        payoffs_ndarray = np.array(payoffs)
        if payoffs_ndarray.ndim == 3:  # bimatrix game
            self.bimatrix = payoffs_ndarray
            self.matrices = [payoffs_ndarray[:, :, 0],
                             payoffs_ndarray[:, :, 1].T]
        elif payoffs_ndarray.ndim == 2:  # symmetric game
            try:
                self.bimatrix = np.dstack((payoffs_ndarray, payoffs_ndarray.T))
            except ValueError:
                raise Exception('a symmetric game must be a square array')
            self.matrices = [payoffs_ndarray, payoffs_ndarray]
        else:
            raise Exception('the game must be represented by a bimatrix or a square matrix')


def br_corr(mixed_str, payoff_mat):
    vec = np.dot(payoff_mat, mixed_str)
    return [i for i, value in enumerate(vec) if value == vec.max()]


def pure2mixed(size, index):
    vec = np.zeros(size)
    vec[index] = 1.0
    return vec


class Players:
    def __init__(self, normal_form_game_2p):
        self.players = normal_form_game_2p.players
        self.matrices = normal_form_game_2p.matrices
        self.num_actions = [
            self.matrices[player].shape[0] for player in self.players
            ]

    def init_beliefs(self):
        self.current_beliefs = [
            np.random.dirichlet(np.ones(self.num_actions[player]))
            for player in self.players
            ]

    def play(self):
        actions = [
            np.random.choice(
                br_corr(self.current_beliefs[player], self.matrices[player])
                )
            for player in self.players
            ]
        self.pure_actions = actions
        self.mixed_actions = [
            pure2mixed(self.num_actions[player], actions[player])
            for player in self.players
            ]


class FictitiousPlayUpdatingPlayers(Players):
    def update_beliefs(self, t):
        self.current_beliefs = [
            self.current_beliefs[player] +
            (1/(t+2)) * (self.mixed_actions[1-player] - self.current_beliefs[player])
            for player in self.players
            ]


class FictitiousPlay:
    def __init__(self, players):
        players.init_beliefs()

    def __call__(self, num_ts):
        for t in range(num_ts):
            yield players.current_beliefs
            players.play()
            players.update_beliefs(t)


def main():
    MATCHING_PENNIES = [[( 1, -1), (-1,  1)],
                        [(-1,  1), ( 1, -1)]]

    COORDINATION_GAME = [[4, 0],
                         [3, 2]]

    T = 5000

    g = NormalFormGame_2P(MATCHING_PENNIES)
    # g = NormalFormGame_2P(COORDINATION_GAME)
    players = FictitiousPlayUpdatingPlayers(g)

    fp = FictitiousPlay(players)

    belief_seqs = [[beliefs[player][1] for player in players.players] for beliefs in fp(T)]
    
    fig, ax = plt.subplots()
    ax.set_color_cycle(['b', 'g'])
    ax.plot(belief_seqs, linewidth=2)
    ax.set_ylim(0, 1)
    plt.show()


if __name__ == '__main__':
    import matplotlib.pyplot as plt

    main()
