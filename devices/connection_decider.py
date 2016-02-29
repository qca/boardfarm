import ser2net_connection
import local_serial_connection

def connection(conn_type, device, **kwargs):
    '''
    Depending on the given model, return an object of the appropriate class type.

    Different boards are flashed with different commands, have
    different memory addresses, and must be handled differently.
    '''
    if conn_type in ("ser2net"):
        return ser2net_connection.Ser2NetConnection(device=device,**kwargs)

    if conn_type in ("local_serial"):
        return local_serial_connection.LocalSerialConnection(device=device,**kwargs)

    # Default for all other models
    print("\nWARNING: Unknown connection type  '%s'." % type)
    print("Please check spelling, or write an appropriate class "
          "to handle that kind of board.")
    return ser2net_connection.Ser2NetConnection(**kwargs)
