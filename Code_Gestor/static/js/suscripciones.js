// Script para mostrar las notificaciones (toast)
document.addEventListener('DOMContentLoaded', function () {
  if (document.querySelector('.toast')) {
    var toastElList = [].slice.call(document.querySelectorAll('.toast'));
    toastElList.forEach(function (toastEl) {
      var toast = new bootstrap.Toast(toastEl);
      toast.show();
    });
  }
});

// Validación del campo "costo" al agregar suscripción
document.addEventListener('DOMContentLoaded', function () {
  const costoInput = document.getElementById('costo');

  costoInput.addEventListener('input', function () {
    let valueWithoutDot = this.value.replace('.', '');

    if (valueWithoutDot.length > 10) {
      valueWithoutDot = valueWithoutDot.slice(0, 10);

      if (this.value.includes('.')) {
        this.value =
          valueWithoutDot.slice(0, valueWithoutDot.length - 2) +
          '.' +
          valueWithoutDot.slice(valueWithoutDot.length - 2);
      } else {
        this.value = valueWithoutDot;
      }
    }
  });

  const form = document.getElementById('formAgregar');
  form.addEventListener('submit', function (event) {
    const costoValor = costoInput.value.replace('.', '').trim();
    if (costoValor.length > 10) {
      event.preventDefault();
      alert("El costo no puede tener más de 10 dígitos.");
    }
  });
});

// Configuración para el modal de edición
document.addEventListener('DOMContentLoaded', function () {
  const editarModal = document.getElementById('editarModal');
  editarModal.addEventListener('show.bs.modal', function (event) {
    const button = event.relatedTarget;

    const id = button.getAttribute('data-id');
    const servicio = button.getAttribute('data-servicio');
    const costo = button.getAttribute('data-costo');
    const fecha = button.getAttribute('data-fecha');
    const categoria = button.getAttribute('data-categoria');
    const activo = button.getAttribute('data-activo') === 'True';

    document.getElementById('editar_id').value = id;
    document.getElementById('editar_servicio').value = servicio;
    document.getElementById('editar_costo').value = costo;
    document.getElementById('editar_fecha').value = fecha;
    document.getElementById('editar_categoria').value = categoria;
    document.getElementById('editar_activo').checked = activo;

    // Referencia para cambiar el texto y el color
    const estadoTexto = document.getElementById('estado_activo_texto');
    if (activo) {
      estadoTexto.textContent = 'Activa';
      estadoTexto.classList.remove('bg-danger');
      estadoTexto.classList.add('bg-success');
    } else {
      estadoTexto.textContent = 'Vencida';
      estadoTexto.classList.remove('bg-success');
      estadoTexto.classList.add('bg-danger');
    }

    // Cambiar el estado activo
    document.getElementById('editar_activo').addEventListener('change', function () {
      if (this.checked) {
        estadoTexto.textContent = 'Activa';
        estadoTexto.classList.remove('bg-danger');
        estadoTexto.classList.add('bg-success');
      } else {
        estadoTexto.textContent = 'Vencida';
        estadoTexto.classList.remove('bg-success');
        estadoTexto.classList.add('bg-danger');
      }
    });

    const form = document.getElementById('formEditar');
    form.action = `/suscripciones/editar/${id}/`;

    const costoEditarInput = document.getElementById('editar_costo');
    costoEditarInput.addEventListener('input', function () {
      let valueWithoutDot = this.value.replace('.', '');

      if (valueWithoutDot.length > 10) {
        valueWithoutDot = valueWithoutDot.slice(0, 10);

        if (this.value.includes('.')) {
          this.value =
            valueWithoutDot.slice(0, valueWithoutDot.length - 2) +
            '.' +
            valueWithoutDot.slice(valueWithoutDot.length - 2);
        } else {
          this.value = valueWithoutDot;
        }
      }
    });

    form.addEventListener('submit', function (event) {
      const costoValor = costoEditarInput.value.replace('.', '').trim();
      if (costoValor.length > 10) {
        event.preventDefault();
        alert("El costo no puede tener más de 10 dígitos.");
      }
    });
  });
});

// Confirmación antes de eliminar una suscripción
document.querySelectorAll('.btn-eliminar').forEach((button) => {
  button.addEventListener('click', function (e) {
    const form = this.closest('.form-eliminar');

    Swal.fire({
      title: '¿Estás seguro?',
      text: 'Esta acción no se puede deshacer',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#6c757d',
      confirmButtonText: 'Sí, eliminar',
      cancelButtonText: 'Cancelar',
    }).then((result) => {
      if (result.isConfirmed) {
        form.submit();
      }
    });
  });
});
