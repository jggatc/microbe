from __future__ import division
import pygame


diag_message = []


def monitor(matrix,control,print_message):
    fps_ave = []
    for i in range(1000):
        fps_ave.append(40)
    while not control.quit:
        if control.clock.get_fps() > 20:
            pygame.display.update(matrix.update_list)
        else:
            pygame.display.flip()
        matrix.update()
        control.update()
        report(matrix,control,print_message,fps_ave)


def report(matrix,control,print_message,fps_ave):
    fps_ave.pop(0)
    fps_ave.append(int(control.clock.get_fps()))
    fps = sum(fps_ave)//len(fps_ave)
    print_message.add("FPS:", fps)
    if matrix.bug_tag:
        try:
            if 1: print_message.add("#:", matrix.bug_tag.species.count)
            if 1: print_message.add("ID:", matrix.bug_tag.identity)
            if 1: print_message.add(matrix.bug_tag.x, matrix.bug_tag.y)
            if 0: print_message.add("S:", matrix.bug_tag.sense())
            if 1: print_message.add("T:", matrix.bug_tag.exist)
            if 1: print_message.add("E:", '%0.1f'%matrix.bug_tag.ingest)
            if 1: print_message.add(list(matrix.bug_tag.gene.values()))
            if 0: print_message.add(matrix.bug_tag.direction)
            if 0: print_message.add(matrix.bug_tag.sense_bacteria)
            if 0: print_message.add(matrix.bug_tag.sensing)
            if 0: print_message.add(matrix.bug_tag.growth_rate)
        except AttributeError:
            pass
    try:
        print_message()
    except:
        pass


def profile():
    import cProfile
    import pstats
    import sys
    cProfile.run('main()', 'profile')
    p = pstats.Stats('profile')
    p.strip_dirs().sort_stats('time').print_stats(25)
    if diag_message:
        print()
        for message in diag_message:
            print(message)
    sys.exit()

