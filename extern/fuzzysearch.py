'''
    Fuzzy matching based on Sublime Text's fuzzy matching algorithm.
'''

__title__ = 'fuzzy-py'
__version__ = '0.3.0'
__author__ = 'Benedikt Schatz'
__license__ = 'Apache 2.0'

from copy import copy
from functools import total_ordering
import re

BONUS_CONSECUTIVE = 16
BONUS_WORD_START = 24
PENALTY_DISTANCE = 4


@total_ordering
class Match:
    '''A single 'path' of patterns characters in the given search string.
    '''

    def __init__(self, score=0, matches=None):
        '''

        :param score: Score for this `Match`.
        :param matches: List of char indices.

        '''
        self.score = score
        self.matches = matches if matches else []

    def __lt__(self, other):
        return self.score < other.score

    def calc_score(self):
        '''Calculate match score for this path.

        :returns: The score.

        '''
        self.score = calc_score(self.matches)
        return self.score

    @property
    def continuous_matches(self):
        '''Group the individual indices into continuous matches.

        :returns: A (start, length) pair for every group.

        '''
        groups = []

        current_start = 0
        current_len = 0

        last_index = -10
        is_first_index = True

        for index in self.matches:
            if not is_first_index and index - 1 == last_index:
                current_len += 1
            else:
                if current_len > 0:
                    groups.append((current_start, current_len))
                current_start = index
                current_len = 1

                is_first_index = False
            last_index = index

        # Make sure to add last group if it isn't empty.
        if current_len > 0:
            groups.append((current_start, current_len))

        return groups

    def __repr__(self):
        return f'Match({self.score}, {self.matches})'


class FuzzySearch:
    def __init__(self, pattern, string,
                 bonus_consecutive=BONUS_CONSECUTIVE,
                 bonus_word_start=BONUS_WORD_START,
                 penalty_distance=PENALTY_DISTANCE):
        '''

        :param pattern: Pattern to search for.
        :param string: Search content to search in.
        :param bonus_consecutive: Bonus for every consecutive match.
        :param penalty_distance: Penalty for every char that is not in pattern.

        '''
        # Current chain.
        self.index_stack = []
        # Scores for every step.
        self.score_stack = []
        # Consecutive match chain length for every step.
        self.consec_len_stack = []

        self.best_match = Match(-999999)

        self.pattern = pattern.lower()  #TSN: allow case-insensitive search
        self.pattern_len = len(pattern)

        self.charmap = build_charmap(string.lower())  #TSN: allow case-insensitive search

        self.bonus_consecutive = bonus_consecutive
        self.penalty_distance = penalty_distance

    def find_best_match(self):
        '''Find the best fuzzy match.

        :returns: The `Match` with the highest match score.

        '''
        self._start_traversal()
        return self.best_match

    def _start_traversal(self):
        '''Start traversing the possible routes `self.pattern` can have in
        `self.string`.
        '''
        pattern_char = self.pattern[0]

        # Get occurences for first char and start traversal from these.
        occurences = find_occurences(pattern_char, self.charmap, 0)

        for o in occurences:
            self._traverse(1, o)

    def _traverse(self, pattern_index=0, offset=0):
        '''Traverse one level along a path.

        Can branch off multiple times for each level.

        '''
        self.index_stack.append(offset)

        # Distance between this and the last match.
        try:
            dist = offset - self.index_stack[-2]
        except IndexError:
            # If there is no previous entry, it's the first element and doesn't
            # have a distance.
            dist = 0

        # Score for this step.
        new_score = 0

        if dist == 0:
            # First match.
            self.consec_len_stack.append(0)
            self.score_stack.append(0)
        elif dist == 1:
            # Consecutive match. Increment consecutive counter and add to new
            # score.
            consec_len = self.consec_len_stack[-1] + 1
            consec_score = consec_len * self.bonus_consecutive
            self.consec_len_stack.append(consec_len)

            new_score = self.score_stack[-1] + consec_score
            self.score_stack.append(new_score)
        else:
            # Any other match. Subtract distance penalty from score.
            self.consec_len_stack.append(0)

            new_score = (
                self.score_stack[-1] - ((dist - 1) * self.penalty_distance)
            )
            self.score_stack.append(new_score)

        # Check if we can even reach the current best score in this path. If we
        # cannot, don't follow this path further.
        max_left_score = max_score(
            self.pattern_len - (len(self.index_stack) - 1),
            self.consec_len_stack[-1]
        )

        # Maximum possible score is lower than our current best's score. Abort.
        if new_score + max_left_score < self.best_match.score:
            self._pop_all()
            return

        # Get the char to look for.
        try:
            pattern_char = self.pattern[pattern_index]
        except IndexError:
            # No char left, score and return.
            self._score_current()
            self._pop_all()
            return

        # Get all occurences after the current position in the target string.
        occurences = find_occurences(pattern_char, self.charmap, offset + 1)

        # No occurences for this char, but we're not finished with the pattern
        # yet so don't score, just return.
        if not occurences:
            self._pop_all()
            return

        # Branch off for every occurence.
        for o in occurences:
            self._traverse(pattern_index + 1, o)

        self._pop_all()

    def _pop_all(self):
        '''Pop all stacks to go one step back.
        '''
        self.index_stack.pop()
        self.consec_len_stack.pop()
        self.score_stack.pop()

    def _score_current(self):
        '''Score the current path and set `self.best_match` if a better match
        is found.
        '''
        current_score = self.score_stack[-1]
        if current_score > self.best_match.score:
            new_best_match = Match(current_score, copy(self.index_stack))
            self.best_match = new_best_match


def find_best_match(pattern, string):
    '''Find the best match for `pattern` in `string`.

    :param pattern: Pattern to look for in `string`.
    :param string: Content to be searched.
    :returns: `Match` with the highest match score.

    '''
    # Filter out whitespace to reduce paths.
    condensed = re.sub(r'\s+', '', pattern)

    search = FuzzySearch(condensed, string)

    return search.find_best_match()


def format(string, match, before, after):
    '''Wraps all matches in `string` in tags.

    :param string: The string to format (should also be the searched string).
    :param match: The resulting `Match` of a fuzzy search.
    :param before: The string to prepend before matches.
    :param after: The string to append after matches.
    :returns: The formatted string.

    '''
    pieces = []

    last_end = 0

    for start, length in match.continuous_matches:
        # Last match end to this match start.
        pieces.append(string[last_end:start])
        pieces.append(before)
        # This match.
        pieces.append(string[start:start + length])
        pieces.append(after)

        last_end = start + length

    # Any left-over characters.
    if last_end != len(string):
        pieces.append(string[last_end:])

    return ''.join(pieces)


def calc_score(positions):
    '''Calculate match score of the given positions.

    :param positions: List of indices.
    :returns: Match score.

    '''
    score = 0
    last_pos = 0
    is_first_pos = True

    current_consecutive_score = 0
    consec_chain_len = 0

    for pos in positions:
        if is_first_pos:
            last_pos = pos
            is_first_pos = False
            continue

        dist = pos - last_pos

        if dist == 1:
            # Consecutive match.
            consec_chain_len += 1
            current_consecutive_score += BONUS_CONSECUTIVE
            score += consec_chain_len * BONUS_CONSECUTIVE
        else:
            score -= (dist - 1) * PENALTY_DISTANCE
            consec_chain_len = 0

        last_pos = pos

    return score


def max_score(num_positions, consec_chain_len=0):
    # Consecutive score doesn't apply to first element, so subtract 1.
    num_for_tri = num_positions - 1 + consec_chain_len

    triangular = num_for_tri * (num_for_tri + 1) // 2

    # Assume we have the best possible combination, which is, currently, just
    # consecutive positions.
    max_consecutive_score = triangular * BONUS_CONSECUTIVE
    # As they are consecutive the distance penalty is 0 and there are no other
    # scoring factors.
    return max_consecutive_score


def find_occurences(c, charmap, offset=0):
    '''Get all occurences for `c` after `offset` in `charmap`.

    :param c: Character to find.
    :param charmap: Dictionary of `char` => [occurences] pairs.
    :param offset: Ignore any occurences before the offset.
    :returns: List of occurences.

    '''
    if c in charmap:
        return (i for i in charmap[c] if i >= offset)
    else:
        return []


def build_charmap(string):
    '''Build a map of `char` => [occurences] pairs.

    :param string: String to decompose.
    :returns: Dictionary of `char` => [occurences] pairs.

    '''
    charmap = {}
    for index, char in enumerate(string):
        if char in charmap:
            charmap[char].append(index)
        else:
            charmap[char] = [index]

    return charmap


def get_subword_starts(string, delimiter_expr=r'\W'):
    is_delim = re.compile(delimiter_expr)

    starts = []

    last_is_upper = False
    last_is_start = False
    last_is_word = False

    for i, c in enumerate(string):
        is_upper = c.istitle()
        is_word_char = is_delim.match(c) is None

        if i == 0:
            last_is_upper = is_upper
            last_is_word = is_word_char
            if is_word_char:
                starts.append(i)
                last_is_start = True
            continue

        if last_is_start:
            last_is_start = False
            last_is_upper = is_upper
            last_is_word = is_word_char
            continue

        if is_word_char and last_is_word and last_is_upper != is_upper:
            # If case is not the same a new subword started.
            starts.append(i)
            last_is_start = True
        elif not last_is_word and is_word_char:
            # Last char was a non-word char and this one is a word char.
            starts.append(i)
            last_is_start = True
        else:
            last_is_start = False

        last_is_upper = is_upper
        last_is_word = is_word_char

    return starts
