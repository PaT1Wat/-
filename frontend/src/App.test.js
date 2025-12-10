import { render, screen } from '@testing-library/react';
import App from './App';

test('renders app header', () => {
  render(<App />);
  // Test that the app renders without crashing
  expect(document.querySelector('.app')).toBeInTheDocument();
});
