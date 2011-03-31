"""\
Hypergraph - core classes.

@author: Aaron Mavrinac
@organization: University of Windsor
@contact: mavrin1@uwindsor.ca
@license: LGPL-3
"""

class Edge(frozenset):
    """\
    Edge class.
    """
    def __new__(cls, edge, head=None):
        """\
        Constructor. Verifies the immutability of the vertices.

        @param edge: Initializing iterable.
        @type edge: C{object}
        @param head: Head vertex (optional).
        @type head: C{object}
        """
        try:
            assert all([vertex.__hash__ for vertex in edge])
        except (AttributeError, AssertionError):
            raise TypeError('vertices must be immutable')
        if not edge:
            raise ValueError('edge must contain at least one vertex')
        return frozenset.__new__(cls, edge)

    def __init__(self, edge, head=None):
        """\
        Constructor. Verifies and sets the head vertex if applicable.

        @param edge: Initializing iterable.
        @type edge: C{object}
        @param head: Head vertex (optional).
        @type head: C{object}
        """
        try:
            assert not head or head in self
        except AssertionError:
            raise ValueError('edge has no vertex %s' % head)
        self._head = head

    def __hash__(self):
        """\
        Hash function.
        """
        return super(Edge, self).__hash__() + \
            (self.head and self.head.__hash__() or 0)

    def __eq__(self, other):
        """\
        Equality operator.
        """
        return frozenset.__eq__(self, other) and self.head is other.head

    def __repr__(self):
        """\
        Canonical string representation.
        """
        if self.head:
            return '%s(%s, \'%s\')' % \
                (self.__class__.__name__, list(self), self.head)
        else:
            return super(Edge, self).__repr__()

    @property
    def head(self):
        """\
        Edge head.
        """
        return self._head

    @property
    def tail(self):
        """\
        Edge tail set.
        """
        return set(self) - set([self._head])


class Hypergraph(object):
    """\
    Hypergraph class.
    """
    def __init__(self, vertices=None, edges=None, weights=None, directed=False):
        """\
        Constructor.

        @param vertices: Initial set of vertices.
        @type vertices: C{set}
        @param edges: Initial set of edges.
        @type edges: C{set}
        @param weights: Initial weight relation.
        @type weights: C{dict}
        @param directed: Directedness of this hypergraph.
        @type directed: C{bool}
        """
        vertices = vertices and set(vertices) or set()
        edges = edges and set(edges) or set()
        self._directed = directed
        try:
            assert all([vertex.__hash__ for vertex in vertices])
        except (AttributeError, AssertionError):
            raise TypeError('vertices must be immutable')
        self._vertices = vertices
        self.weights = {}
        try:
            for edge in edges:
                assert isinstance(edge, Edge)
                assert all([vertex in vertices for vertex in edge])
                assert (not directed and not edge.head) \
                    or (directed and edge.head)
                try:
                    self.weights[edge] = float(weights[edge])
                except (KeyError, TypeError):
                    self.weights[edge] = 1.0
        except AssertionError:
            raise ValueError('invalid edge %s' % edge)
        except TypeError:
            pass
        self._edges = edges

    def __eq__(self, other):
        """\
        Equality operator.
        """
        return self.vertices == other.vertices and self.edges == other.edges \
            and all([abs(self.weights[edge] - other.weights[edge]) < 1e-4 \
            for edge in self.edges])

    def __repr__(self):
        """\
        Canonical string representation.
        """
        return '%s(vertices=%s, edges=%s, weights=%s, directed=%s)' % \
            (self.__class__.__name__, self.vertices, self.edges, self.weights,
             self.directed)

    def add_vertex(self, vertex):
        """\
        Add a vertex to this hypergraph.

        @param vertex: The vertex object to add.
        @type vertex: C{object}
        """
        try:
            assert vertex.__hash__
        except (AttributeError, AssertionError):
            raise TypeError('vertex must be immutable')
        self._vertices.add(vertex)

    def remove_vertex(self, vertex):
        """\
        Remove a vertex and all incident edges from this hypergraph.

        @param vertex: The vertex object to remove.
        @type vertex: C{object}
        """
        edges = set(self.edges)
        for edge in edges:
            if vertex in edge:
                self.remove_edge(edge)
        self._vertices.remove(vertex)

    def add_edge(self, edge, weight=1.0):
        """\
        Add an edge to this hypergraph.

        @param edge: The edge to add.
        @type edge: L{Edge}
        @param weight: The weight of the edge.
        @type weight: C{float}
        """
        try:
            assert isinstance(edge, Edge)
            assert all([vertex in self.vertices for vertex in edge])
            assert (not self.directed and not edge.head) \
                or (self.directed and edge.head)
        except AssertionError:
            raise ValueError('invalid edge %s' % edge)
        self._edges.add(edge)
        self.weights[edge] = weight

    def remove_edge(self, edge):
        """\
        Remove an edge from this hypergraph.

        @param edge: The edge to add.
        @type edge: L{Edge}
        """
        del self.weights[edge]
        self._edges.remove(edge)

    @property
    def directed(self):
        """\
        Directedness of the hypergraph.
        """
        return self._directed

    @property
    def vertices(self):
        """\
        Vertex set of the hypergraph.
        """
        return self._vertices

    @property
    def edges(self):
        """\
        Edge set of the hypergraph.
        """
        return self._edges

    def uniform(self, k):
        """\
        Return whether this is a k-uniform hypergraph.

        @param k: The value of k.
        @type k: C{int}
        @return: Uniformity.
        @rtype: C{bool}
        """
        return all([len(edge) == k for edge in self.edges])

    def adjacent(self, u, v):
        """\
        Return whether two vertices are adjacent (directly connected by a
        hyperedge). Does not consider the direction of the hyperedge.

        @param u: The first vertex.
        @type u: C{object}
        @param v: The second vertex.
        @type v: C{object}
        @return: Adjacency.
        @rtype: C{bool}
        """
        return any([(u in edge and v in edge) for edge in self.edges])

    def incident(self, tail, head):
        """\
        Return whether there exists a directed hyperedge from the tail vertex
        to the head vertex.

        @param tail: The tail vertex.
        @type tail: C{object}
        @param head: The head vertex.
        @type head: C{object}
        @return: Incidence.
        @rtype: C{bool}
        """
        if self.directed:
            return any([(tail in edge and head in edge and edge.head == head) \
                for edge in self.edges])
        else:
            return self.adjacent(tail, head)

    def neighbors(self, vertex):
        """\
        Return the set of vertices which are adjacent (in an undirected
        hypergraph) or incident (in a directed hypergraph) to a given vertex.

        @param vertex: The vertex.
        @type vertex: C{object}
        @return: The set of vertices adjacent to the vertex.
        @rtype: C{set}
        """
        return set([v for v in self.vertices if self.incident(vertex, v)]) \
            - set([vertex])

    def degree(self, vertex, weighted=True):
        """\
        Return the (weighted) degree of the given vertex.

        @param vertex: The vertex.
        @type vertex: C{object}
        @param weighted: Return the weighted degree if true.
        @type weighted: C{bool}
        @return: Degree of the vertex.
        @rtype: C{float}
        """
        return sum([weighted and self.weights[edge] or 1 for edge \
            in self.edges if vertex in edge])

    def indegree(self, vertex, weighted=True):
        """\
        Return the (weighted) indegree of the given vertex.

        @param vertex: The vertex.
        @type vertex: C{object}
        @param weighted: Return the weighted indegree if true.
        @type weighted: C{bool}
        @return: Indegree of the vertex.
        @rtype: C{float}
        """
        if not self.directed:
            return self.degree(vertex, weighted)
        return sum([weighted and self.weights[edge] or 1 for edge \
            in self.edges if edge.head == vertex])
        
    def outdegree(self, vertex, weighted=True):
        """\
        Return the (weighted) outdegree of the given vertex.

        @param vertex: The vertex.
        @type vertex: C{object}
        @param weighted: Return the weighted outdegree if true.
        @type weighted: C{bool}
        @return: Outdegree of the vertex.
        @rtype: C{float}
        """
        if not self.directed:
            return self.degree(vertex, weighted)
        return sum([weighted and self.weights[edge] or 1 for edge \
            in self.edges if vertex in edge and edge.head != vertex])
        

class Graph(Hypergraph):
    """\
    Graph (2-uniform hypergraph) class.
    """
    def __init__(self, vertices=None, edges=None, weights=None, directed=False):
        """\
        Constructor.

        @param vertices: Initial set of vertices.
        @type vertices: C{set}
        @param edges: Initial set of edges.
        @type edges: C{set}
        @param weights: Initial weight relation.
        @type weights: C{dict}
        @param directed: Directedness of this graph.
        @type directed: C{bool}
        """
        try:
            assert all([len(edge) == 2 for edge in edges])
        except AssertionError:
            raise ValueError('edges must have exactly two vertices')
        except TypeError:
            pass
        super(Graph, self).__init__(vertices, edges, weights, directed)

    def uniform(self, k):
        """\
        Return whether this is a k-uniform hypergraph.

        @param k: The value of k.
        @type k: C{int}
        """
        return k == 2
