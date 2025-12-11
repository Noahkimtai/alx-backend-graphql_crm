import graphene
from crm.schema import Query as CRMQuery, Mutation as CRMMutation


# class Query(graphene.ObjectType):
#     """
#     This class will handle queries
#     """

#     hello = graphene.String()

#     def resolve_hello(root, info):
#         return "Hello, GraphQL!"


class Query(CRMQuery, graphene.ObjectType):
    """
    This class will handle queries
    """

    pass

class Mutation(CRMMutation, graphene.ObjectType):
    """
    This class will handle mutations
    """
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
