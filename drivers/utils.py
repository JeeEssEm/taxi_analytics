from orders.models import TaxiOrder


def get_available_driver_actions(current_status):
    cancel_action = {
        'action': 'CANCELLED',
        'label': 'Отменить заказ',
        'description': '',
        'color': 'red',
        'icon': '❌',
        'requires_confirmation': True
    }

    actions_map = {
        TaxiOrder.StatusChoices.WAITING_FOR_DRIVER: [
            {
                'action': 'DRIVER_WAITING',
                'label': 'Я на месте',
                'description': 'Уведомить клиента о прибытии',
                'color': 'purple',
                'icon': '📍'
            },
            cancel_action

        ],
        TaxiOrder.StatusChoices.DRIVER_WAITING: [
            {
                'action': 'ON_THE_WAY',
                'label': 'Начать поездку',
                'description': 'Клиент сел в машину, начинаем поездку',
                'color': 'indigo',
                'icon': '🛣️'
            },
            cancel_action
        ],
        TaxiOrder.StatusChoices.ON_THE_WAY: [
            {
                'action': 'DONE',
                'label': 'Завершить поездку',
                'description': 'Клиент доехал до места назначения',
                'color': 'green',
                'icon': '🏁',
                'requires_confirmation': True
            },
            cancel_action
        ]
    }
    return actions_map.get(current_status, [])
