// src/components/DeletarUsuario.js

import React, { useState } from 'react';
import './DeletarUsuario.css'; // Vamos criar este arquivo para estilização

function DeletarUsuario({ userEmail, onAccountDeleted }) {
  // Estado para controlar a visibilidade da área de confirmação
  const [showConfirm, setShowConfirm] = useState(false);
  
  // Estado para armazenar a senha digitada pelo usuário
  const [password, setPassword] = useState('');

  // Estados para feedback visual (carregamento e erros)
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Função chamada ao clicar no botão inicial "Excluir Conta"
  const handleInitialDeleteClick = () => {
    setShowConfirm(true); // Mostra a seção de confirmação
    setError(null); // Limpa erros antigos
  };

  // Função para cancelar a exclusão
  const handleCancel = () => {
    setShowConfirm(false);
    setPassword(''); // Limpa o campo de senha
  };

  // Função que realmente envia a requisição para a API
  const handleConfirmDelete = async () => {
    if (!password) {
      setError("Por favor, digite sua senha para confirmar.");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:5000/api/user', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: userEmail,
          password: password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        // Se a resposta não for OK (ex: erro 401, 500), lança um erro
        throw new Error(data.error || 'Falha ao excluir a conta.');
      }
      
      // Se deu tudo certo
      alert('Sua conta foi excluída com sucesso.');
      onAccountDeleted(); // Chama a função do componente pai para deslogar o usuário

    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="delete-account-container">
      <h2>Gerenciamento da Conta</h2>
      
      {!showConfirm ? (
        // 1. Botão inicial
        <button onClick={handleInitialDeleteClick} className="delete-button-initial">
          Excluir Minha Conta
        </button>
      ) : (
        // 2. Área de confirmação
        <div className="confirmation-box">
          <h4>Confirmar Exclusão de Conta</h4>
          <p className="warning-text">
            <strong>AVISO:</strong> Esta ação é permanente e irreversível. Todos os seus dados, incluindo seus dispositivos cadastrados, serão removidos.
          </p>
          <label htmlFor="password">Para confirmar, digite sua senha:</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Sua senha"
          />

          {error && <p className="error-message">{error}</p>}
          
          <div className="button-group">
            <button onClick={handleCancel} disabled={isLoading} className="cancel-button">
              Cancelar
            </button>
            <button onClick={handleConfirmDelete} disabled={isLoading} className="confirm-delete-button">
              {isLoading ? 'Excluindo...' : 'Confirmar Exclusão'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default DeletarUsuario;