import graphene


class Query(graphene.ObjectType):
    """
    This class will handle queries
    """

    hello = graphene.String()

    def resolve_hello(root, info):
        return "Hello, GraphQL!"


schema = graphene.Schema(query=Query)
