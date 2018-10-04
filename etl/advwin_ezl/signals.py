from django.dispatch import Signal, receiver

new_person = Signal(providing_args=["person", "created"])


@receiver(new_person)
def create_person(person, created, **kwargs):
    if created:
        person.save()
    elif person.id:
        person.save(update_fields=[
            'alter_date', 'legal_name', 'name', 'is_lawyer', 'legal_type',
            'cpf_cnpj', 'alter_user', 'is_active', 'is_customer', 'is_supplier'
        ])


class temp_disconnect_signal():
    """ Temporarily disconnect a model from a signal """

    def __init__(self, signal, receiver, sender, dispatch_uid=None):
        self.signal = signal
        self.receiver = receiver
        self.sender = sender
        self.dispatch_uid = dispatch_uid

    def __enter__(self):
        self.signal.disconnect(
            receiver=self.receiver,
            sender=self.sender,
            dispatch_uid=self.dispatch_uid,
            weak=False)

    def __exit__(self, type, value, traceback):
        self.signal.connect(
            receiver=self.receiver,
            sender=self.sender,
            dispatch_uid=self.dispatch_uid,
            weak=False)
