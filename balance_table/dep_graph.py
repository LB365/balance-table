def find_parents(x, input_data):
    res = []
    new = input_data[x]
    while new != []:
        res.extend([i for i in new if i not in res])
        temp = []
        for i in res:
            if input_data.get(i):
                temp.extend(input_data.get(i))
        new = [k for k in temp if k not in res]
    return res


def find_dep_graph(dependency_graph):
    output_parents = {i: find_parents(i, dependency_graph)
                      for i in dependency_graph}
    output_childrens = {k: [] for k in dependency_graph.keys()}
    for x in dependency_graph:
        for child, parents in output_parents.items():
            for parent in parents:
                if x == parent:
                    output_childrens[x].append(child)
    return dict(filter(lambda v: v[1], output_childrens.items()))


if __name__ == '__main__':
    dependency_graph = {
        '1': [],
        '2': ['1'],
        '3': ['2'],
        '4': ['1'],
    }
    expected = {'1': ['2', '3', '4'], '2': ['3']}
    result = find_dep_graph(dependency_graph)
    assert result == expected
