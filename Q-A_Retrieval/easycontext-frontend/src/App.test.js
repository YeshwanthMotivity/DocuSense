import { render, screen } from '@testing-library/react';
import App from './App';

test('should render a link to learn React', () => {
  render(<App />);
  const linkElement = screen.getByRole('link', { name: /learn react/i });
  expect(linkElement).toBeInTheDocument();
});