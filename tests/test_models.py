from tests.client import *



def test_load_user(client):
    User1=load_user(1)
    expected_value=(1,'pili',pw,"user")
    value=(User1.id,User1.username,User1.password,User1.role)
    assert value==expected_value
    User2=load_user(2)
    assert User2==None

    