import { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

export default function Signup() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const navigate = useNavigate();
  

  const handleSignup = async () => {
    if (password !== confirmPassword) {
      alert("비밀번호가 일치하지 않습니다.");
      return;
    }

    try {
      const res = await axios.post('http://localhost:5000/api/signup', {
        email, password
      });
      if (res.data.success) {
        alert("회원가입 성공!");
        navigate("/");
      } else {
        alert("회원가입 실패: " + res.data.message);
      }
    } catch (err) {
      alert("에러 발생: " + err.message);
    }
  };

  return (
    <div className="App">
      <div className='signup-form'>
        <h2>회원가입</h2>
      <input
        type="email"
        placeholder="이메일"
        onChange={(e) => setEmail(e.target.value)}
      />
      <input
        type="password"
        placeholder="비밀번호"
        onChange={(e) => setPassword(e.target.value)}
      />
      <input
        type="password"
        placeholder="비밀번호 확인"
        onChange={(e) => setConfirmPassword(e.target.value)}
      />
      <button onClick={handleSignup}>회원가입</button>
      </div>
      <p><a href="/">로그인으로 돌아가기</a></p>
    </div>
  );
}
