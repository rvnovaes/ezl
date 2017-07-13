from django.dispatch import Signal, receiver

new_person = Signal(providing_args=["person", "created"])


@receiver(new_person)
def create_person(person, created, **kwargs):
    if created:
        person.save()
    elif person.id:
        person.save(update_fields=['alter_date',
                                   'legal_name',
                                   'name',
                                   'is_lawyer',
                                   'is_correspondent',
                                   'is_court',
                                   'legal_type',
                                   'cpf_cnpj',
                                   'alter_user',
                                   'is_active',
                                   'is_customer',
                                   'is_supplier'])


        # @receiver(post_save)
        # def create_person2(sender,instance,created,**kwargs)
        #
