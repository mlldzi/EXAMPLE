import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';

// Скрипт для анимации нажатия кнопок
document.addEventListener('DOMContentLoaded', () => {
  // Функция для добавления анимации нажатия на кнопки
  const addButtonPressAnimation = () => {
    // Находим все кнопки с классом btn
    const buttons = document.querySelectorAll('.btn');
    
    // Добавляем обработчик события клика для каждой кнопки
    buttons.forEach(button => {
      button.addEventListener('click', (e) => {
        // Удаляем класс анимации, если он уже есть
        button.classList.remove('btn-animate-press');
        
        // Форсируем перерисовку DOM
        void button.offsetWidth;
        
        // Добавляем класс анимации
        button.classList.add('btn-animate-press');
        
        // Удаляем класс анимации после её завершения
        setTimeout(() => {
          button.classList.remove('btn-animate-press');
        }, 400); // Время анимации из CSS
      });
    });
  };

  // Функция для добавления анимации нажатия на кнопки выбора файла
  const addFileButtonAnimation = () => {
    // Находим все кнопки выбора файла
    const fileLabels = document.querySelectorAll('.file-upload-label');
    
    fileLabels.forEach(label => {
      label.addEventListener('click', (e) => {
        // Находим кнопку внутри label
        const button = label.querySelector('.file-upload-button');
        if (button) {
          // Удаляем класс анимации, если он уже есть
          button.classList.remove('file-upload-button-animate');
          
          // Форсируем перерисовку DOM
          void button.offsetWidth;
          
          // Добавляем класс анимации
          button.classList.add('file-upload-button-animate');
          
          // Удаляем класс анимации после её завершения
          setTimeout(() => {
            button.classList.remove('file-upload-button-animate');
          }, 400); // Время анимации из CSS
        }
      });
    });
  };
  
  // Запускаем функции сразу и повторно через небольшой интервал,
  // чтобы обработать динамически созданные элементы
  const initAnimations = () => {
    addButtonPressAnimation();
    addFileButtonAnimation();
  };
  
  initAnimations();
  
  // Периодически проверяем и добавляем обработчики для новых элементов
  setInterval(initAnimations, 2000);
});

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </React.StrictMode>
); 