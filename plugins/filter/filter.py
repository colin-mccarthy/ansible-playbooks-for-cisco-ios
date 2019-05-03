#!/usr/bin/python
class FilterModule:

    @staticmethod
    def filters():
        return {
            'bgp_as_from_rt': FilterModule.bgp_as_from_rt
        }

    @staticmethod
    def bgp_as_from_rt(rt_list):
        bgp_as_list = []
        for my_rt in rt_list:
            rt_halves = my_rt.split(':')
            bgp_as_list.append(int(rt_halves[0]))

        return bgp_as_list
