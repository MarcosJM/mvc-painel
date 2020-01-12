from datetime import date


class Deputy:

    def __init__(self, picture_url, id_register, parliamentary_name, name, sex, born_in, died_in, profession,
                 schooling, email, state, party, current_status, party_affiliations, periods_in_exercise):

        self.picture_url = picture_url
        self.id_register = id_register
        self.parliamentary_name = parliamentary_name
        self.name = name
        self.sex = sex
        self.born_in = born_in
        self.died_in = died_in
        self.profession = profession
        self.schooling = schooling
        self.email = email
        self.state = state
        self.party = party
        self.current_status = current_status
        self.party_affiliations = party_affiliations
        self.periods_in_exercise = periods_in_exercise

    # returns deputy age
    def getAge(self):
        today = date.today()
        age = today.year - self.born_in.year - ((today.month, today.day) < (self.born_in.month, self.born_in.day))
        return age
