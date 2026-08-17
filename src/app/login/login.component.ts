import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { AuthService } from '../services/auth.service';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {
  loginForm!: FormGroup;
  loading = false;
  submitted = false;
  returnUrl!: string;
  hidePassword = true;
  errorMessage = '';

  // Demo credentials info
  demoAccounts = [
    { username: 'admin', password: 'admin123', role: 'Administrator' },
    { username: 'user', password: 'user123', role: 'User' },
    { username: 'operator', password: 'operator123', role: 'Operator' }
  ];

  constructor(
    private formBuilder: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private authService: AuthService,
    private snackBar: MatSnackBar
  ) {
    // Redirect to home if already logged in
    if (this.authService.isAuthenticated) {
      this.router.navigate(['/']);
    }
  }

  ngOnInit(): void {
    this.loginForm = this.formBuilder.group({
      username: ['', Validators.required],
      password: ['', Validators.required]
    });

    // Get return url from route parameters or default to '/'
    this.returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/';
  }

  get f() {
    return this.loginForm.controls;
  }

  onSubmit(): void {
    this.submitted = true;
    this.errorMessage = '';

    if (this.loginForm.invalid) {
      return;
    }

    this.loading = true;

    this.authService.login(this.f['username'].value, this.f['password'].value)
      .subscribe({
        next: (success) => {
          if (success) {
            this.snackBar.open('Login successful!', 'Close', {
              duration: 3000,
              horizontalPosition: 'end',
              verticalPosition: 'top',
              panelClass: ['success-snackbar']
            });
            this.router.navigate([this.returnUrl]);
          } else {
            this.errorMessage = 'Invalid username or password';
            this.loading = false;
          }
        },
        error: () => {
          this.errorMessage = 'An error occurred during login';
          this.loading = false;
        }
      });
  }

  useDemoAccount(username: string, password: string): void {
    this.loginForm.patchValue({ username, password });
  }
}
