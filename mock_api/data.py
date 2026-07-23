from __future__ import annotations

from datetime import date, timedelta


def generate_appointments(total: int = 50) -> list[dict[str, str]]:
    """Gera agendamentos determinísticos para permitir paginação e filtros ricos."""
    patients = [
        "Ana Souza",
        "Bruno Alves",
        "Carla Mendes",
        "Diego Martins",
        "Elisa Ramos",
        "Felipe Nogueira",
        "Gabriela Rocha",
        "Henrique Lima",
        "Isabela Costa",
        "Joao Pedro",
    ]
    doctors = [
        "Dr. Carlos Lima",
        "Dra. Marina Costa",
        "Dr. Felipe Rocha",
        "Dra. Beatriz Silva",
        "Dr. Lucas Almeida",
    ]
    specialties = [
        "Cardiologia",
        "Pediatria",
        "Dermatologia",
        "Ortopedia",
        "Oftalmologia",
    ]
    insurance_plans = [
        "VidaSaude",
        "ClinMais",
        "SaudePrime",
        "BemCare",
        "MaisVida",
    ]
    statuses = ["Confirmado", "Pendente", "Cancelado"]

    base_date = date(2026, 7, 22)
    appointments: list[dict[str, str]] = []
    for index in range(total):
        appointment_date = (base_date + timedelta(days=index // 5)).isoformat()
        hour = 8 + (index % 10)
        minute = "00" if index % 2 == 0 else "30"
        cpf_number = 11122233000 + index

        appointments.append(
            {
                "data": appointment_date,
                "horario": f"{hour:02d}:{minute}",
                "paciente": f"{patients[index % len(patients)]} {index + 1}",
                "cpf": f"{cpf_number:011d}",
                "medico": doctors[index % len(doctors)],
                "especialidade": specialties[index % len(specialties)],
                "convenio": insurance_plans[index % len(insurance_plans)],
                "status": statuses[index % len(statuses)],
            }
        )

    return appointments


APPOINTMENTS = generate_appointments(total=50)
